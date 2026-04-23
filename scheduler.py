import pytz
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from aiogram import Bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import date
import database as db
from config import CHAT_ID, MORNING_HOUR, EVENING_HOUR, TIMEZONE


async def send_morning_reminder(bot: Bot):
    habits = await db.get_habits()
    if not habits:
        return

    today = str(date.today())
    logs = await db.get_today_logs(today)
    done_count = sum(1 for h in habits if logs.get(h["id"], False))

    builder = InlineKeyboardBuilder()
    for habit in habits:
        done = logs.get(habit["id"], False)
        mark = "✅" if done else "⬜"
        builder.button(
            text=f"{mark} {habit['name']}",
            callback_data=f"toggle:{habit['id']}:{today}",
        )
    builder.adjust(2)

    await bot.send_message(
        CHAT_ID,
        f"☀️ *Доброе утро!*\n\n"
        f"Привычки на {today} — выполнено {done_count}/{len(habits)}.\n\n"
        f"Нажми чтобы отметить:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown",
    )


async def send_evening_reminder(bot: Bot):
    habits = await db.get_habits()
    if not habits:
        return

    today = str(date.today())
    logs = await db.get_today_logs(today)

    done = [h for h in habits if logs.get(h["id"], False)]
    missed = [h for h in habits if not logs.get(h["id"], False)]
    pct = round(len(done) / len(habits) * 100)

    lines = [
        "🌙 *Итог дня*\n",
        f"✅ Выполнено: {len(done)}/{len(habits)} ({pct}%)",
    ]
    if missed:
        missed_names = ", ".join(h["name"] for h in missed)
        lines.append(f"❌ Пропущено: {missed_names}")

    keyboard = None
    if missed:
        builder = InlineKeyboardBuilder()
        for h in missed:
            builder.button(
                text=f"⬜ {h['name']}",
                callback_data=f"toggle:{h['id']}:{today}",
            )
        builder.adjust(2)
        keyboard = builder.as_markup()
    else:
        lines.append("\n🎉 Все привычки выполнены!")

    await bot.send_message(
        CHAT_ID,
        "\n".join(lines),
        reply_markup=keyboard,
        parse_mode="Markdown",
    )


def setup_scheduler(bot: Bot) -> AsyncIOScheduler:
    tz = pytz.timezone(TIMEZONE)
    scheduler = AsyncIOScheduler(timezone=tz)

    scheduler.add_job(
        send_morning_reminder,
        CronTrigger(hour=MORNING_HOUR, minute=0, timezone=tz),
        args=[bot],
        id="morning_reminder",
        replace_existing=True,
    )
    scheduler.add_job(
        send_evening_reminder,
        CronTrigger(hour=EVENING_HOUR, minute=0, timezone=tz),
        args=[bot],
        id="evening_reminder",
        replace_existing=True,
    )

    return scheduler
