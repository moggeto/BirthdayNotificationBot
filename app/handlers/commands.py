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


def register_command_handlers(dp: Dispatcher):
    dp.message.register(start_command, Command("start"))