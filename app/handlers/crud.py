from aiogram import types, Dispatcher
from aiogram.filters import Command
from app.database.session import Session
from app.database.models import Birthday
from app.keyboards.reply import main_menu

async def start_command(message: types.Message):
    await message.answer("Привет! Я бот для напоминаний о днях рождения.", reply_markup=main_menu)


async def add_birthday(message: types.Message):
    args = message.text.split(maxsplit=4)
    if len(args) < 4:
        await message.reply(
            "Используй формат: /add <Имя> <Фамилия> <День> <Месяц>\nПример: /add Анна Иванова 15 7"
        )
        return

    first_name, last_name, day, month = args[1], args[2], args[3], args[4]
    session = Session()

    try:
        day, month = int(day), int(month)
        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError("Неверный формат данных.")

        new_birthday = Birthday(
            user_id=message.from_user.id,
            first_name=first_name,
            last_name=last_name,
            day=day,
            month=month,
        )
        session.add(new_birthday)
        session.commit()
        await message.reply(f"День рождения {first_name} {last_name} добавлен!")
    except Exception as e:
        await message.reply("Ошибка при добавлении: " + str(e))
    finally:
        session.close()


async def list_birthdays(message: types.Message):
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
    except Exception as e:
        await message.reply(f"Произошла ошибка: {e}")
    finally:
        session.close()


async def remove_birthday(message: types.Message):
    args = message.text.split(maxsplit=2)
    if len(args) < 3:
        await message.reply("Используй формат: /remove <Имя> <Фамилия>\nПример: /remove Анна Иванова")
        return

    first_name, last_name = args[1], args[2]
    session = Session()

    try:
        birthday = session.query(Birthday).filter_by(
            user_id=message.from_user.id, first_name=first_name, last_name=last_name
        ).first()
        if not birthday:
            await message.reply(f"Запись с именем {first_name} {last_name} не найдена.")
            return

        session.delete(birthday)
        session.commit()
        await message.reply(f"День рождения {first_name} {last_name} успешно удален.")
    except Exception as e:
        await message.reply(f"Ошибка при удалении: {e}")
    finally:
        session.close()


def register_crud_handlers(dp: Dispatcher):
    """
    Регистрирует все хендлеры для работы с CRUD.
    """
    dp.message.register(start_command, Command("start"))
    dp.message.register(add_birthday, Command("add"))
    dp.message.register(list_birthdays, Command("list"))
    dp.message.register(remove_birthday, Command("remove"))
