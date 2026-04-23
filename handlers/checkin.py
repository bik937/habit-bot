from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import date
import database as db

router = Router()


def build_checkin_keyboard(
    habits: list[dict], logs: dict[int, bool], target_date: str
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for habit in habits:
        done = logs.get(habit["id"], False)
        mark = "✅" if done else "⬜"
        builder.button(
            text=f"{mark} {habit['name']}",
            callback_data=f"toggle:{habit['id']}:{target_date}",
        )
    builder.adjust(1)
    return builder.as_markup()


def checkin_text(habits: list[dict], logs: dict[int, bool], target_date: str) -> str:
    done_count = sum(1 for h in habits if logs.get(h["id"], False))
    return (
        f"📋 *Привычки на {target_date}*\n"
        f"Выполнено: {done_count}/{len(habits)}\n\n"
        f"Нажми чтобы отметить:"
    )


@router.message(Command("checkin"))
async def cmd_checkin(message: Message):
    today = str(date.today())
    habits = await db.get_habits()

    if not habits:
        await message.answer("Нет привычек. Добавь их через /manage")
        return

    logs = await db.get_today_logs(today)
    await message.answer(
        checkin_text(habits, logs, today),
        reply_markup=build_checkin_keyboard(habits, logs, today),
        parse_mode="Markdown",
    )


@router.callback_query(lambda c: c.data and c.data.startswith("toggle:"))
async def callback_toggle(call: CallbackQuery):
    _, habit_id_str, date_str = call.data.split(":")
    habit_id = int(habit_id_str)

    await db.toggle_log(habit_id, date_str)

    habits = await db.get_habits()
    logs = await db.get_today_logs(date_str)

    await call.message.edit_text(
        checkin_text(habits, logs, date_str),
        reply_markup=build_checkin_keyboard(habits, logs, date_str),
        parse_mode="Markdown",
    )
    await call.answer()
