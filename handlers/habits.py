from aiogram import Router, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder
import database as db

router = Router()


class AddHabitState(StatesGroup):
    waiting_for_name = State()


def build_manage_keyboard() -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    builder.button(text="➕ Добавить привычку", callback_data="habit_add")
    builder.button(text="🗑 Удалить привычку", callback_data="habit_delete_list")
    builder.button(text="📋 Список привычек", callback_data="habit_list")
    builder.adjust(1)
    return builder.as_markup()


@router.message(Command("manage"))
@router.message(F.text == "⚙️ Manage")
async def cmd_manage(message: Message):
    await message.answer(
        "⚙️ *Управление привычками*\n\nЧто хочешь сделать?",
        reply_markup=build_manage_keyboard(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data == "habit_add")
async def callback_habit_add(call: CallbackQuery, state: FSMContext):
    await state.set_state(AddHabitState.waiting_for_name)
    await call.message.answer("Введи название новой привычки:")
    await call.answer()


@router.message(AddHabitState.waiting_for_name)
async def process_habit_name(message: Message, state: FSMContext):
    name = message.text.strip() if message.text else ""
    if not name:
        await message.answer("Название не может быть пустым. Попробуй ещё раз:")
        return

    success = await db.add_habit(name)
    await state.clear()

    if success:
        await message.answer(
            f"✅ Привычка *{name}* добавлена!\n\n/manage — вернуться в меню",
            parse_mode="Markdown",
        )
    else:
        await message.answer(
            f"⚠️ Привычка *{name}* уже существует.",
            parse_mode="Markdown",
        )


@router.callback_query(F.data == "habit_list")
async def callback_habit_list(call: CallbackQuery):
    habits = await db.get_habits()
    if not habits:
        await call.message.answer("Нет активных привычек. Добавь через /manage")
        await call.answer()
        return

    lines = [f"{i + 1}. {h['name']}" for i, h in enumerate(habits)]
    text = "📋 *Твои привычки:*\n\n" + "\n".join(lines)
    await call.message.answer(text, parse_mode="Markdown")
    await call.answer()


@router.callback_query(F.data == "habit_delete_list")
async def callback_delete_list(call: CallbackQuery):
    habits = await db.get_habits()
    if not habits:
        await call.message.answer("Нет привычек для удаления.")
        await call.answer()
        return

    builder = InlineKeyboardBuilder()
    for h in habits:
        builder.button(text=f"🗑 {h['name']}", callback_data=f"habit_del:{h['id']}")
    builder.button(text="← Назад", callback_data="habit_back")
    builder.adjust(1)

    await call.message.answer(
        "Выбери привычку для удаления:",
        reply_markup=builder.as_markup(),
    )
    await call.answer()


@router.callback_query(F.data.startswith("habit_del:"))
async def callback_delete_habit(call: CallbackQuery):
    habit_id = int(call.data.split(":")[1])
    habits = await db.get_habits()
    habit = next((h for h in habits if h["id"] == habit_id), None)

    await db.delete_habit(habit_id)
    name = habit["name"] if habit else "Привычка"

    await call.message.edit_text(f"🗑 *{name}* удалена.", parse_mode="Markdown")
    await call.answer()


@router.callback_query(F.data == "habit_back")
async def callback_back(call: CallbackQuery):
    await call.message.edit_text(
        "⚙️ *Управление привычками*\n\nЧто хочешь сделать?",
        reply_markup=build_manage_keyboard(),
        parse_mode="Markdown",
    )
    await call.answer()
