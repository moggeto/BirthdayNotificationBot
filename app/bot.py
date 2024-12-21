from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from app.config import BOT_TOKEN
from app.handlers import crud, notify

bot = Bot(token=BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())