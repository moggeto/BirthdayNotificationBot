from aiogram import types, Dispatcher
from app.database.session import Session
from app.database.models import Birthday


async def handle_text_message(message: types.Message):
    if message.text == "Добавить день рождения":
        await message.reply(
            "Отправьте данные в формате: /add <Имя> <Фамилия> <День> <Месяц>\nПример: /add Анна Иванова 15 7"
        )
    elif message.text == "Список дней рождений":
        session = Session()
        try:
            birthdays = session.query(Birthday).filter_by(user_id=message.from_user.id).all()
            if not birthdays:
                await message.reply("У вас пока нет добавленных дней рождений.")
                return

            response = "Ваши дни рождения:\n"
            for birthday in birthdays:
                response += f"- {birthday.first_name} {birthday.last_name}: {birthday.day:02}.{birthday.month:02}\n"
            await message.reply(response)
        finally:
            session.close()
    elif message.text == "Редактировать день рождения":
        await message.reply(
            "Отправьте данные в формате: /edit <Имя> <Фамилия> <Новый день> <Новый месяц>\nПример: /edit Анна Иванова 20 12"
        )
    elif message.text == "Настройки":
        await message.reply("Настройки пока недоступны.")
    else:
        await message.reply("Неизвестная команда. Используйте кнопки на клавиатуре.")

def register_text_handlers(dp: Dispatcher):
    """
    Регистрирует обработчики текстовых сообщений.
    """
    dp.message.register(handle_text_message)