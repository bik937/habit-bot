import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN: str = os.environ["BOT_TOKEN"]
CHAT_ID: int = int(os.environ["CHAT_ID"])
DB_PATH: str = os.getenv("DB_PATH", "data/habits.db")
MORNING_HOUR: int = int(os.getenv("MORNING_HOUR", "9"))
EVENING_HOUR: int = int(os.getenv("EVENING_HOUR", "21"))
TIMEZONE: str = os.getenv("TIMEZONE", "Europe/Moscow")
