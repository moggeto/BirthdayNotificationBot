from aiogram import types, Dispatcher
from aiogram.filters import Command

from app.database.session import get_session
from app.keyboards.reply import main_menu
from app.services.users import get_or_create_user


async def start_command(message: types.Message):
    with get_session() as session:
        get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
        )

    await message.answer(
        "Привет! Я бот для напоминаний о днях рождения.",
        reply_markup=main_menu,
    )

async def info_command(message: types.Message):
    await message.answer(
        "Этот бот помогает не забывать о днях рождения.\n\n"
        "Что он умеет:\n"
        "- Добавлять дни рождения\n"
        "- Хранить имя, дату, год (опционально)\n"
        "- Добавлять заметки (например идеи подарков)\n"
        "- Напоминать заранее (за несколько дней)\n"
        "- Поддерживать несколько уведомлений (например за 7 и за 1 день)\n\n"
        "Основные команды:\n"
        "/start — открыть меню\n"
        "/info — информация о боте"
    )

def register_command_handlers(dp: Dispatcher):
    dp.message.register(start_command, Command("start"))
    dp.message.register(info_command, Command("info"))