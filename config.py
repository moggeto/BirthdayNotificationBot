import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///birthdays.db")
PAGE_SIZE = 10

# Scheduler
NOTIFICATION_CHECK_HOUR = int(os.getenv("NOTIFICATION_CHECK_HOUR", "9"))
NOTIFICATION_CHECK_MINUTE = int(os.getenv("NOTIFICATION_CHECK_MINUTE", "0"))