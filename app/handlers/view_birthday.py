from aiogram import Dispatcher, types, Bot
from aiogram.types import CallbackQuery

from app.database.session import get_session
from app.keyboards.inline import get_pagination_keyboard
from app.services.birthdays import get_user_birthdays
from app.services.users import get_or_create_user
from config import PAGE_SIZE


async def fetch_birthdays(telegram_id: int, full_name: str, sort_by: str = "name"):
    with get_session() as session:
        user = get_or_create_user(session, telegram_id=telegram_id, name=full_name)
        return get_user_birthdays(session, user, sort_by)


async def send_paginated_list(
    bot: Bot,
    chat_id: int,
    birthdays: list,
    page: int,
    total_pages: int,
    sort_by: str,
):
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    items = birthdays[start:end]

    response = "Список дней рождений:\n"
    response += "\n".join(
        f"- {birthday.first_name} {birthday.last_name}".rstrip() + f": {birthday.day:02}.{birthday.month:02}"
        + (f".{birthday.year}" if birthday.year else "")
        for birthday in items
    )

    keyboard = get_pagination_keyboard(page, total_pages, sort_by)
    await bot.send_message(chat_id, response, reply_markup=keyboard)


async def show_birthdays(message: types.Message):
    birthdays = await fetch_birthdays(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
    )

    if not birthdays:
        await message.reply("У вас пока нет добавленных дней рождений.")
        return

    page = 1
    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE
    await send_paginated_list(message.bot, message.chat.id, birthdays, page, total_pages, "name")


async def handle_pagination(callback: CallbackQuery):
    data = callback.data.split(":")
    page = int(data[1])
    sort_by = data[2]

    birthdays = await fetch_birthdays(
        telegram_id=callback.from_user.id,
        full_name=callback.from_user.full_name,
        sort_by=sort_by,
    )
    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE

    await send_paginated_list(callback.bot, callback.message.chat.id, birthdays, page, total_pages, sort_by)
    await callback.answer()


async def handle_sort(callback: CallbackQuery):
    sort_by = callback.data.split(":")[1]

    birthdays = await fetch_birthdays(
        telegram_id=callback.from_user.id,
        full_name=callback.from_user.full_name,
        sort_by=sort_by,
    )

    if not birthdays:
        await callback.answer("Список пуст.")
        return

    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE
    await send_paginated_list(callback.bot, callback.message.chat.id, birthdays, 1, total_pages, sort_by)
    await callback.answer()


def register_view_handlers(dp: Dispatcher):
    dp.message.register(show_birthdays, lambda message: message.text == "Просмотр дней рождений")
    dp.callback_query.register(handle_pagination, lambda c: c.data.startswith("pagination"))
    dp.callback_query.register(handle_sort, lambda c: c.data.startswith("sort"))