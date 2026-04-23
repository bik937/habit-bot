from aiogram import Router, F
from aiogram.filters import Command, or_f
from aiogram.types import Message, CallbackQuery, BufferedInputFile
from aiogram.utils.keyboard import InlineKeyboardBuilder
from datetime import date
import database as db
import charts

router = Router()


@router.message(or_f(Command("today"), F.text == "📋 Today"))
async def cmd_today(message: Message):
    today = str(date.today())
    habits = await db.get_habits()

    if not habits:
        await message.answer("Нет привычек. Добавь через /manage")
        return

    logs = await db.get_today_logs(today)
    done = [h for h in habits if logs.get(h["id"], False)]
    missed = [h for h in habits if not logs.get(h["id"], False)]
    pct = round(len(done) / len(habits) * 100)

    lines = [f"📋 *Сводка за {today}*\n", f"✅ Выполнено: {len(done)}/{len(habits)} ({pct}%)\n"]

    if done:
        lines.append("*Выполнено:*")
        for h in done:
            lines.append(f"  ✅ {h['name']}")

    if missed:
        lines.append("\n*Не выполнено:*")
        for h in missed:
            lines.append(f"  ❌ {h['name']}")

    if not missed:
        lines.append("\n🎉 Все привычки выполнены!")

    await message.answer("\n".join(lines), parse_mode="Markdown")


@router.message(or_f(Command("stats"), F.text == "📊 Stats"))
async def cmd_stats(message: Message):
    builder = InlineKeyboardBuilder()
    builder.button(text="📅 7 дней", callback_data="stats:7")
    builder.button(text="📅 30 дней", callback_data="stats:30")
    builder.button(text="📅 90 дней", callback_data="stats:90")
    builder.adjust(3)

    await message.answer(
        "📊 *Статистика*\n\nВыбери период:",
        reply_markup=builder.as_markup(),
        parse_mode="Markdown",
    )


@router.callback_query(F.data.startswith("stats:"))
async def callback_stats(call: CallbackQuery):
    days = int(call.data.split(":")[1])

    habits = await db.get_habits()
    if not habits:
        await call.answer("Нет данных для статистики.", show_alert=True)
        return

    await call.answer(f"Строю графики за {days} дней...")
    await call.message.answer(f"⏳ Генерирую статистику за {days} дней...")

    heatmap = await charts.generate_heatmap(days)
    if heatmap:
        await call.message.answer_photo(
            BufferedInputFile(heatmap.read(), filename="heatmap.png"),
            caption=f"🗓 Тепловая карта — {days} дней",
        )

    trend = await charts.generate_trend(days)
    if trend:
        await call.message.answer_photo(
            BufferedInputFile(trend.read(), filename="trend.png"),
            caption=f"📈 Прогресс выполнения — {days} дней",
        )

    top = await charts.generate_top_habits(days)
    if top:
        await call.message.answer_photo(
            BufferedInputFile(top.read(), filename="top.png"),
            caption=f"🏆 Рейтинг привычек — {days} дней",
        )
