from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.filters import Command
from app.database.session import Session
from app.database.models import Birthday
from app.keyboards.reply import main_menu, confirm_menu, cancel_menu
from app.states.birthday_states import BirthdayStates


async def start_command(message: types.Message):
    await message.answer("Привет! Я бот для напоминаний о днях рождения.", reply_markup=main_menu)



# async def list_birthdays(message: types.Message):
#     session = Session()
#     try:
#         birthdays = session.query(Birthday).filter_by(user_id=message.from_user.id).all()
#         if not birthdays:
#             await message.reply("У вас пока нет добавленных дней рождений.")
#             return
#
#         response = "Ваши дни рождения:\n"
#         for birthday in birthdays:
#             response += f"- {birthday.first_name} {birthday.last_name}: {birthday.day:02}.{birthday.month:02}\n"
#         await message.reply(response)
#     except Exception as e:
#         await message.reply(f"Произошла ошибка: {e}")
#     finally:
#         session.close()





def register_command_handlers(dp: Dispatcher):
    """
    Регистрирует все хендлеры для работы с CRUD.
    """
    dp.message.register(start_command, Command("start"))

