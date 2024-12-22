from aiogram import Dispatcher, types, Bot
from aiogram.types import CallbackQuery
from app.database.models import Birthday
from app.keyboards.inline import get_pagination_keyboard
from app.database.session import Session
from config import PAGE_SIZE


async def fetch_birthdays(user_id: int, sort_by: str = "name") -> list[Birthday]:
    """
    Извлекает дни рождения из базы данных для указанного пользователя с сортировкой.
    """
    session = Session()
    try:
        query = session.query(Birthday).filter_by(user_id=user_id)
        if sort_by == "name":
            query = query.order_by(Birthday.first_name)
        elif sort_by == "date":
            query = query.order_by(Birthday.month, Birthday.day)
        return query.all()
    finally:
        session.close()


async def send_paginated_list(
    bot: Bot,
    chat_id: int,
    birthdays: list[Birthday],
    page: int,
    total_pages: int,
    sort_by: str
):
    """
    Отправляет пагинированный список дней рождений с клавиатурой.
    """
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    items = birthdays[start:end]

    response = "Список дней рождений:\n"
    response += "\n".join(
        f"- {birthday.first_name} {birthday.last_name}: {birthday.day:02}.{birthday.month:02}"
        for birthday in items
    )

    keyboard = get_pagination_keyboard(page, total_pages, sort_by)
    await bot.send_message(chat_id, response, reply_markup=keyboard)


async def show_birthdays(message: types.Message):
    """
    Отображает список дней рождений с первой страницы.
    """
    user_id = message.from_user.id
    birthdays = await fetch_birthdays(user_id)

    if not birthdays:
        await message.reply("У вас пока нет добавленных дней рождений.")
        return

    page = 1
    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE
    await send_paginated_list(message.bot, message.chat.id, birthdays, page, total_pages, "name")


async def handle_pagination(callback: CallbackQuery):
    """
    Обрабатывает нажатия кнопок пагинации.
    """
    data = callback.data.split(":")
    page = int(data[1])
    sort_by = data[2]
    user_id = callback.from_user.id

    birthdays = await fetch_birthdays(user_id, sort_by)
    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE
    await send_paginated_list(callback.bot, callback.message.chat.id, birthdays, page, total_pages, sort_by)
    await callback.answer()


async def handle_sort(callback: CallbackQuery):
    """
    Обрабатывает сортировку списка дней рождений.
    """
    sort_by = callback.data.split(":")[1]
    user_id = callback.from_user.id

    birthdays = await fetch_birthdays(user_id, sort_by)
    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE
    await send_paginated_list(callback.bot, callback.message.chat.id, birthdays, 1, total_pages, sort_by)
    await callback.answer()


def register_view_handlers(dp: Dispatcher):
    """
    Регистрирует хендлеры для просмотра и управления списком дней рождений.
    """
    dp.message.register(show_birthdays, lambda message: message.text == "Просмотр дней рождений")
    dp.callback_query.register(handle_pagination, lambda c: c.data.startswith("pagination"))
    dp.callback_query.register(handle_sort, lambda c: c.data.startswith("sort"))
