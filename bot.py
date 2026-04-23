import asyncio
import logging

from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import Message

from config import BOT_TOKEN
from database import init_db
from scheduler import setup_scheduler
from handlers import habits, checkin, stats

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())

dp.include_router(habits.router)
dp.include_router(checkin.router)
dp.include_router(stats.router)


@dp.message(Command("start"))
async def cmd_start(message: Message):
    await message.answer(
        "👋 Привет! Я твой личный трекер привычек.\n\n"
        "Что умею:\n"
        "⚙️ /manage — добавить или удалить привычки\n"
        "✅ /checkin — отметить привычки за сегодня\n"
        "📊 /stats — статистика и графики\n"
        "📋 /today — сводка за сегодня\n\n"
        "Начни с /manage — добавь первые привычки!"
    )


async def main():
    await init_db()
    logging.info("База данных инициализирована")

    scheduler = setup_scheduler(bot)
    scheduler.start()
    logging.info("Планировщик запущен")

    try:
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    finally:
        scheduler.shutdown()
        await bot.session.close()


if __name__ == "__main__":
    asyncio.run(main())
