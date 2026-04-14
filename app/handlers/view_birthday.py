from aiogram import Dispatcher, types, Bot
from aiogram.types import CallbackQuery
from sqlalchemy.orm import selectinload

from app.database.models import Birthday, BirthdayDate, CalendarType, DateDisplayFormat, HebrewMonth
from app.database.session import get_session
from app.keyboards.inline import get_pagination_keyboard
from app.services.users import get_or_create_user
from config import PAGE_SIZE


HEBREW_MONTH_LABELS = {
    HebrewMonth.tishrei: "Тишрей",
    HebrewMonth.cheshvan: "Хешван",
    HebrewMonth.kislev: "Кислев",
    HebrewMonth.tevet: "Тевет",
    HebrewMonth.shevat: "Шват",
    HebrewMonth.adar: "Адар",
    HebrewMonth.adar_i: "Адар I",
    HebrewMonth.adar_ii: "Адар II",
    HebrewMonth.nisan: "Нисан",
    HebrewMonth.iyar: "Ияр",
    HebrewMonth.sivan: "Сиван",
    HebrewMonth.tammuz: "Таммуз",
    HebrewMonth.av: "Ав",
    HebrewMonth.elul: "Элул",
}


def get_gregorian_date(birthday: Birthday) -> BirthdayDate | None:
    for item in birthday.dates:
        if item.calendar_type == CalendarType.gregorian:
            return item
    return None


def get_hebrew_date(birthday: Birthday) -> BirthdayDate | None:
    for item in birthday.dates:
        if item.calendar_type == CalendarType.hebrew:
            return item
    return None


def format_gregorian_date(date_item: BirthdayDate | None) -> str:
    if not date_item or not date_item.g_day or not date_item.g_month:
        return "не указана"

    text = f"{date_item.g_day:02}.{date_item.g_month:02}"
    if date_item.g_year:
        text += f".{date_item.g_year}"
    return text


def format_hebrew_date(date_item: BirthdayDate | None) -> str:
    if not date_item or not date_item.h_day or not date_item.h_month:
        return "не указана"

    month_label = HEBREW_MONTH_LABELS.get(date_item.h_month, str(date_item.h_month))
    text = f"{date_item.h_day} {month_label}"
    if date_item.h_year:
        text += f" {date_item.h_year}"
    return text


def format_dates_block(birthday: Birthday, display_format: DateDisplayFormat) -> str:
    gregorian = get_gregorian_date(birthday)
    hebrew = get_hebrew_date(birthday)

    if display_format == DateDisplayFormat.gregorian:
        return f"Дата: {format_gregorian_date(gregorian)}"

    if display_format == DateDisplayFormat.hebrew:
        return f"Дата: {format_hebrew_date(hebrew)}"

    return (
        f"Григорианская: {format_gregorian_date(gregorian)}\n"
        f"Еврейская: {format_hebrew_date(hebrew)}"
    )


def format_birthday_for_list(birthday: Birthday, display_format: DateDisplayFormat) -> str:
    full_name = f"{birthday.first_name} {birthday.last_name}".strip()

    lines = [
        f"- {full_name}",
        f"  {format_dates_block(birthday, display_format)}",
    ]

    if birthday.description:
        lines.append(f"  Описание: {birthday.description}")

    return "\n".join(lines)


def get_sort_key_for_date(birthday: Birthday):
    gregorian = get_gregorian_date(birthday)
    if gregorian and gregorian.g_month and gregorian.g_day:
        return 0, gregorian.g_month, gregorian.g_day, birthday.first_name.lower(), birthday.last_name.lower()

    hebrew = get_hebrew_date(birthday)
    if hebrew and hebrew.h_month and hebrew.h_day:
        month_order = list(HebrewMonth).index(hebrew.h_month)
        return 1, month_order, hebrew.h_day, birthday.first_name.lower(), birthday.last_name.lower()

    return 2, 99, 99, birthday.first_name.lower(), birthday.last_name.lower()


def sort_birthdays(birthdays: list[Birthday], sort_by: str) -> list[Birthday]:
    if sort_by == "date":
        return sorted(birthdays, key=get_sort_key_for_date)

    return sorted(
        birthdays,
        key=lambda item: (item.first_name.lower(), item.last_name.lower()),
    )


async def fetch_birthdays(telegram_id: int, full_name: str, sort_by: str = "name"):
    with get_session() as session:
        user = get_or_create_user(session, telegram_id=telegram_id, name=full_name)

        birthdays = (
            session.query(Birthday)
            .options(selectinload(Birthday.dates))
            .filter(Birthday.user_id == user.id)
            .all()
        )

        sorted_birthdays = sort_birthdays(birthdays, sort_by)
        return sorted_birthdays, user.date_display_format


async def send_paginated_list(
    bot: Bot,
    chat_id: int,
    birthdays: list[Birthday],
    display_format: DateDisplayFormat,
    page: int,
    total_pages: int,
    sort_by: str,
):
    start = (page - 1) * PAGE_SIZE
    end = start + PAGE_SIZE
    items = birthdays[start:end]

    response_lines = [f"Список дней рождений (страница {page}/{total_pages}):"]
    response_lines.extend(
        format_birthday_for_list(birthday, display_format) for birthday in items
    )
    response = "\n\n".join(response_lines)

    keyboard = get_pagination_keyboard(page, total_pages, sort_by)
    await bot.send_message(chat_id, response, reply_markup=keyboard)


async def show_birthdays(message: types.Message):
    birthdays, display_format = await fetch_birthdays(
        telegram_id=message.from_user.id,
        full_name=message.from_user.full_name,
    )

    if not birthdays:
        await message.reply("У вас пока нет добавленных дней рождений.")
        return

    page = 1
    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE
    await send_paginated_list(
        bot=message.bot,
        chat_id=message.chat.id,
        birthdays=birthdays,
        display_format=display_format,
        page=page,
        total_pages=total_pages,
        sort_by="name",
    )


async def handle_pagination(callback: CallbackQuery):
    data = callback.data.split(":")
    page = int(data[1])
    sort_by = data[2]

    birthdays, display_format = await fetch_birthdays(
        telegram_id=callback.from_user.id,
        full_name=callback.from_user.full_name,
        sort_by=sort_by,
    )

    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE

    await send_paginated_list(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        birthdays=birthdays,
        display_format=display_format,
        page=page,
        total_pages=total_pages,
        sort_by=sort_by,
    )
    await callback.answer()


async def handle_sort(callback: CallbackQuery):
    sort_by = callback.data.split(":")[1]

    birthdays, display_format = await fetch_birthdays(
        telegram_id=callback.from_user.id,
        full_name=callback.from_user.full_name,
        sort_by=sort_by,
    )

    if not birthdays:
        await callback.answer("Список пуст.")
        return

    total_pages = (len(birthdays) + PAGE_SIZE - 1) // PAGE_SIZE

    await send_paginated_list(
        bot=callback.bot,
        chat_id=callback.message.chat.id,
        birthdays=birthdays,
        display_format=display_format,
        page=1,
        total_pages=total_pages,
        sort_by=sort_by,
    )
    await callback.answer()


def register_view_handlers(dp: Dispatcher):
    dp.message.register(show_birthdays, lambda message: message.text == "Просмотр дней рождений")
    dp.callback_query.register(handle_pagination, lambda c: c.data.startswith("pagination"))
    dp.callback_query.register(handle_sort, lambda c: c.data.startswith("sort"))