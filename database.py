import os
import aiosqlite
from config import DB_PATH


async def init_db():
    dir_name = os.path.dirname(DB_PATH)
    if dir_name:
        os.makedirs(dir_name, exist_ok=True)

    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute("""
            CREATE TABLE IF NOT EXISTS habits (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                emoji TEXT DEFAULT '✅',
                active INTEGER DEFAULT 1,
                position INTEGER DEFAULT 0,
                created_at DATE DEFAULT CURRENT_DATE
            )
        """)
        await db.execute("""
            CREATE TABLE IF NOT EXISTS daily_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                habit_id INTEGER REFERENCES habits(id),
                date DATE NOT NULL,
                done INTEGER DEFAULT 0,
                UNIQUE(habit_id, date)
            )
        """)
        # Миграция: добавить колонку position если её нет
        try:
            await db.execute("ALTER TABLE habits ADD COLUMN position INTEGER DEFAULT 0")
        except Exception:
            pass
        # Инициализировать position для привычек у которых он = 0
        await db.execute("UPDATE habits SET position = id WHERE position = 0")
        await db.commit()


async def get_habits() -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            "SELECT id, name, emoji FROM habits WHERE active = 1 ORDER BY position ASC, id ASC"
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(row) for row in rows]


async def add_habit(name: str, emoji: str = "✅") -> bool:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute(
                "SELECT COALESCE(MAX(position), 0) FROM habits WHERE active = 1"
            ) as cursor:
                row = await cursor.fetchone()
                next_pos = (row[0] if row else 0) + 1
            await db.execute(
                "INSERT INTO habits (name, emoji, position) VALUES (?, ?, ?)",
                (name, emoji, next_pos),
            )
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def move_habit(habit_id: int, direction: str):
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT id, position FROM habits WHERE active = 1 ORDER BY position ASC, id ASC"
        ) as cursor:
            habits = [(r[0], r[1]) for r in await cursor.fetchall()]

        idx = next((i for i, (hid, _) in enumerate(habits) if hid == habit_id), None)
        if idx is None:
            return

        if direction == "up" and idx > 0:
            other_idx = idx - 1
        elif direction == "down" and idx < len(habits) - 1:
            other_idx = idx + 1
        else:
            return

        curr_id, curr_pos = habits[idx]
        other_id, other_pos = habits[other_idx]

        await db.execute("UPDATE habits SET position = ? WHERE id = ?", (other_pos, curr_id))
        await db.execute("UPDATE habits SET position = ? WHERE id = ?", (curr_pos, other_id))
        await db.commit()


async def rename_habit(habit_id: int, new_name: str) -> bool:
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute(
                "UPDATE habits SET name = ? WHERE id = ? AND active = 1",
                (new_name, habit_id),
            )
            await db.commit()
        return True
    except aiosqlite.IntegrityError:
        return False


async def delete_habit(habit_id: int):
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute(
            "UPDATE habits SET active = 0 WHERE id = ?", (habit_id,)
        )
        await db.commit()


async def toggle_log(habit_id: int, date: str) -> int:
    """Цикл состояний: 0 (⬜) → 1 (✅) → 2 (❌) → 0"""
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT done FROM daily_logs WHERE habit_id = ? AND date = ?",
            (habit_id, date),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            new_done = 1
            await db.execute(
                "INSERT INTO daily_logs (habit_id, date, done) VALUES (?, ?, 1)",
                (habit_id, date),
            )
        else:
            current = row[0]
            new_done = 1 if current == 0 else 2 if current == 1 else 0
            await db.execute(
                "UPDATE daily_logs SET done = ? WHERE habit_id = ? AND date = ?",
                (new_done, habit_id, date),
            )
        await db.commit()
    return new_done


async def get_today_logs(date: str) -> dict[int, int]:
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute(
            "SELECT habit_id, done FROM daily_logs WHERE date = ?", (date,)
        ) as cursor:
            rows = await cursor.fetchall()
    return {row[0]: row[1] for row in rows}


async def get_logs_range(start: str, end: str) -> list[dict]:
    async with aiosqlite.connect(DB_PATH) as db:
        db.row_factory = aiosqlite.Row
        async with db.execute(
            """
            SELECT h.id, h.name, h.emoji, dl.date, dl.done
            FROM habits h
            LEFT JOIN daily_logs dl
                ON h.id = dl.habit_id AND dl.date BETWEEN ? AND ?
            WHERE h.active = 1
            ORDER BY h.id, dl.date
            """,
            (start, end),
        ) as cursor:
            rows = await cursor.fetchall()
    return [dict(row) for row in rows]
