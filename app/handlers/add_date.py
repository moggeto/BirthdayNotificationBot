from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from app.database.models import NotificationCalendarMode
from app.database.session import get_session
from app.keyboards.reply import (
    main_menu,
    confirm_menu,
    cancel_menu,
    date_type_menu,
    both_date_mode_menu,
    notification_mode_menu,
    hebrew_months_menu,
)
from app.services.birthdays import (
    create_birthday_gregorian,
    create_birthday_hebrew,
    create_birthday_both,
)
from app.services.date_formatting import format_full
from app.services.hebrew_dates import validate_hebrew_date
from app.services.users import get_or_create_user
from app.states.birthday_states import BirthdayStates
from app.services.validators import (
    parse_date_with_optional_year,
    parse_positive_day,
    parse_optional_positive_year,
    parse_hebrew_month,
)


DATE_TYPE_MAP = {
    "Только григорианская": "gregorian",
    "Только еврейская": "hebrew",
    "Обе даты": "both",
}

BOTH_MODE_MAP = {
    "Автоконвертация из григорианской": "auto",
    "Ввести еврейскую вручную": "manual",
}

NOTIFICATION_MODE_MAP = {
    "Напоминать по григорианской": NotificationCalendarMode.gregorian,
    "Напоминать по еврейской": NotificationCalendarMode.hebrew,
    "Напоминать по обеим": NotificationCalendarMode.both,
}


def build_confirmation_text(data: dict) -> str:
    lines = [
        "Проверь данные:",
        f"Имя и фамилия: {data['name']}",
        f"Тип даты: {data['date_type']}",
    ]

    if data["date_type"] in ("gregorian", "both"):
        g_text = f"{data['g_day']:02}.{data['g_month']:02}"
        if data.get("g_year"):
            g_text += f".{data['g_year']}"
        lines.append(f"Григорианская дата: {g_text}")

    if data["date_type"] == "hebrew":
        h_text = f"{data['h_day']} {data['h_month'].value}"
        if data.get("h_year"):
            h_text += f" {data['h_year']}"
        lines.append(f"Еврейская дата: {h_text}")

    if data["date_type"] == "both":
        if data.get("both_mode") == "auto":
            lines.append("Еврейская дата: будет создана автоконвертацией")
        else:
            h_text = f"{data['h_day']} {data['h_month'].value}"
            if data.get("h_year"):
                h_text += f" {data['h_year']}"
            lines.append(f"Еврейская дата: {h_text}")

    lines.append(
        f"Режим уведомлений: {data['notification_mode'].value}"
    )

    description = data.get("description") or "не указано"
    lines.append(f"Описание: {description}")

    return "\n".join(lines)


async def start_adding_birthday(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Введите имя и фамилию:",
        reply_markup=cancel_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_name)


async def process_name(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await cancel_operation(message, state)
        return

    if not text:
        await message.answer("Имя не может быть пустым. Введите имя ещё раз.")
        return

    await state.update_data(name=text)
    await message.answer(
        "Выбери тип даты:",
        reply_markup=date_type_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_date_type)


async def process_date_type(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await cancel_operation(message, state)
        return

    date_type = DATE_TYPE_MAP.get(text)
    if not date_type:
        await message.answer("Выбери тип даты кнопкой.", reply_markup=date_type_menu)
        return

    await state.update_data(date_type=date_type)

    if date_type == "gregorian":
        await message.answer(
            "Введите григорианскую дату.\nФорматы:\nДД.ММ\nДД.ММ.ГГГГ",
            reply_markup=cancel_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_gregorian_date)
        return

    if date_type == "hebrew":
        await message.answer(
            "Введите еврейский день рождения числом от 1 до 30:",
            reply_markup=cancel_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_hebrew_day)
        return

    await message.answer(
        "Как создать вторую дату?",
        reply_markup=both_date_mode_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_both_mode)


async def process_both_mode(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await message.answer(
            "Выбери тип даты:",
            reply_markup=date_type_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_date_type)
        return

    both_mode = BOTH_MODE_MAP.get(text)
    if not both_mode:
        await message.answer("Выбери вариант кнопкой.", reply_markup=both_date_mode_menu)
        return

    await state.update_data(both_mode=both_mode)

    await message.answer(
        "Введите григорианскую дату.\nФорматы:\nДД.ММ\nДД.ММ.ГГГГ",
        reply_markup=cancel_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_gregorian_date)


async def process_gregorian_date(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        data = await state.get_data()
        if data.get("date_type") == "both":
            await message.answer(
                "Как создать вторую дату?",
                reply_markup=both_date_mode_menu,
            )
            await state.set_state(BirthdayStates.waiting_for_both_mode)
        else:
            await message.answer(
                "Выбери тип даты:",
                reply_markup=date_type_menu,
            )
            await state.set_state(BirthdayStates.waiting_for_date_type)
        return

    try:
        day, month, year = parse_date_with_optional_year(text)
    except ValueError as e:
        await message.answer(str(e))
        return

    await state.update_data(g_day=day, g_month=month, g_year=year)
    data = await state.get_data()

    if data.get("date_type") == "both" and data.get("both_mode") == "auto":
        if year is None:
            await message.answer("Для автоконвертации нужен год. Введи дату в формате ДД.ММ.ГГГГ.")
            return

        await message.answer(
            "Теперь введите описание или '-' если оно не нужно.",
            reply_markup=cancel_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_description)
        return

    if data.get("date_type") == "both" and data.get("both_mode") == "manual":
        await message.answer(
            "Введите еврейский день рождения числом от 1 до 30:",
            reply_markup=cancel_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_hebrew_day)
        return

    await message.answer(
        "Теперь введите описание или '-' если оно не нужно.",
        reply_markup=cancel_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_description)


async def process_hebrew_day(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        data = await state.get_data()

        if data.get("date_type") == "hebrew":
            await message.answer("Выбери тип даты:", reply_markup=date_type_menu)
            await state.set_state(BirthdayStates.waiting_for_date_type)
            return

        if data.get("date_type") == "both":
            await message.answer(
                "Введите григорианскую дату.\nФорматы:\nДД.ММ\nДД.ММ.ГГГГ",
                reply_markup=cancel_menu,
            )
            await state.set_state(BirthdayStates.waiting_for_gregorian_date)
            return

    try:
        day = parse_positive_day(text)
    except ValueError as e:
        await message.answer(str(e))
        return

    await state.update_data(h_day=day)
    await message.answer(
        "Выбери еврейский месяц:",
        reply_markup=hebrew_months_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_hebrew_month)


async def process_hebrew_month(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await message.answer(
            "Введите еврейский день рождения числом от 1 до 30:",
            reply_markup=cancel_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_hebrew_day)
        return

    try:
        month = parse_hebrew_month(text)
    except ValueError as e:
        await message.answer(str(e), reply_markup=hebrew_months_menu)
        return

    await state.update_data(h_month=month)
    await message.answer(
        "Введите еврейский год или '-' если без года:",
        reply_markup=cancel_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_hebrew_year)


async def process_hebrew_year(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await message.answer(
            "Выбери еврейский месяц:",
            reply_markup=hebrew_months_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_hebrew_month)
        return

    try:
        year = parse_optional_positive_year(text)
        data = await state.get_data()
        validate_hebrew_date(data["h_day"], data["h_month"], year)
    except ValueError as e:
        await message.answer(str(e))
        return

    await state.update_data(h_year=year)
    await message.answer(
        "Теперь введите описание или '-' если оно не нужно.",
        reply_markup=cancel_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_description)


async def process_description(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        data = await state.get_data()

        if data.get("date_type") == "gregorian":
            await message.answer(
                "Введите григорианскую дату.\nФорматы:\nДД.ММ\nДД.ММ.ГГГГ",
                reply_markup=cancel_menu,
            )
            await state.set_state(BirthdayStates.waiting_for_gregorian_date)
            return

        if data.get("date_type") == "hebrew":
            await message.answer(
                "Введите еврейский год или '-' если без года:",
                reply_markup=cancel_menu,
            )
            await state.set_state(BirthdayStates.waiting_for_hebrew_year)
            return

        if data.get("date_type") == "both" and data.get("both_mode") == "auto":
            await message.answer(
                "Введите григорианскую дату.\nФорматы:\nДД.ММ\nДД.ММ.ГГГГ",
                reply_markup=cancel_menu,
            )
            await state.set_state(BirthdayStates.waiting_for_gregorian_date)
            return

        await message.answer(
            "Введите еврейский год или '-' если без года:",
            reply_markup=cancel_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_hebrew_year)
        return

    description = "" if text == "-" else text
    await state.update_data(description=description)

    data = await state.get_data()
    date_type = data["date_type"]

    if date_type == "gregorian":
        default_mode = NotificationCalendarMode.gregorian
    elif date_type == "hebrew":
        default_mode = NotificationCalendarMode.hebrew
    else:
        default_mode = NotificationCalendarMode.gregorian

    await state.update_data(notification_mode=default_mode)

    await message.answer(
        "Выбери режим напоминаний:",
        reply_markup=notification_mode_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_notification_mode)


async def process_notification_mode(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await message.answer(
            "Теперь введите описание или '-' если оно не нужно.",
            reply_markup=cancel_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_description)
        return

    mode = NOTIFICATION_MODE_MAP.get(text)
    if not mode:
        await message.answer("Выбери режим кнопкой.", reply_markup=notification_mode_menu)
        return

    data = await state.get_data()
    date_type = data["date_type"]

    if mode == NotificationCalendarMode.gregorian and date_type == "hebrew":
        await message.answer("У записи нет григорианской даты. Выбери другой режим.")
        return

    if mode == NotificationCalendarMode.hebrew and date_type == "gregorian":
        if not data.get("g_year"):
            await message.answer("Еврейской даты здесь не будет. Выбери другой режим.")
            return

    if mode == NotificationCalendarMode.both:
        if date_type == "gregorian":
            await message.answer("Режим по обеим датам доступен только когда у записи действительно есть обе даты.")
            return
        if date_type == "both" and data.get("both_mode") == "auto" and not data.get("g_year"):
            await message.answer("Для обеих дат в режиме автоконвертации нужен год.")
            return

    await state.update_data(notification_mode=mode)
    data = await state.get_data()

    await message.answer(
        build_confirmation_text(data),
        reply_markup=confirm_menu,
    )
    await state.set_state(BirthdayStates.confirmation)


async def confirm_birthday(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await message.answer(
            "Выбери режим напоминаний:",
            reply_markup=notification_mode_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_notification_mode)
        return

    if text != "Подтвердить":
        await message.answer("Нажми 'Подтвердить' или 'Назад'.")
        return

    data = await state.get_data()

    try:
        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )

            if data["date_type"] == "gregorian":
                birthday = create_birthday_gregorian(
                    session=session,
                    user=user,
                    full_name=data["name"],
                    day=data["g_day"],
                    month=data["g_month"],
                    year=data.get("g_year"),
                    description=data.get("description", ""),
                    notification_calendar_mode=data["notification_mode"],
                    auto_create_hebrew=True,
                )
            elif data["date_type"] == "hebrew":
                birthday = create_birthday_hebrew(
                    session=session,
                    user=user,
                    full_name=data["name"],
                    day=data["h_day"],
                    month=data["h_month"],
                    year=data.get("h_year"),
                    description=data.get("description", ""),
                    notification_calendar_mode=data["notification_mode"],
                )
            else:
                birthday = create_birthday_both(
                    session=session,
                    user=user,
                    full_name=data["name"],
                    description=data.get("description", ""),
                    g_day=data["g_day"],
                    g_month=data["g_month"],
                    g_year=data.get("g_year"),
                    notification_calendar_mode=data["notification_mode"],
                    auto_create_hebrew=(data.get("both_mode") == "auto"),
                    h_day=data.get("h_day"),
                    h_month=data.get("h_month"),
                    h_year=data.get("h_year"),
                )

            # ВАЖНО: формируем итоговый текст ПОКА session ещё открыта
            full_name = f"{birthday.first_name} {birthday.last_name}".strip()
            date_text = format_full(birthday, user.date_display_format)
            notification_mode_text = data["notification_mode"].value

        await message.answer(
            f"Добавлено:\n{full_name}\nДата: {date_text}\nРежим уведомлений: {notification_mode_text}",
            reply_markup=main_menu,
        )
        await state.clear()

    except ValueError as e:
        await message.answer(str(e))
    except IntegrityError:
        await message.answer("Такая запись уже существует.")
    except Exception as e:
        await message.answer(f"Ошибка при добавлении: {e}")


async def cancel_operation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Операция отменена. Возвращаю в главное меню.",
        reply_markup=main_menu,
    )


def register_add_handlers(dp: Dispatcher):
    dp.message.register(
        start_adding_birthday,
        lambda message: message.text == "Добавить день рождения",
    )
    dp.message.register(process_name, BirthdayStates.waiting_for_name)
    dp.message.register(process_date_type, BirthdayStates.waiting_for_date_type)
    dp.message.register(process_both_mode, BirthdayStates.waiting_for_both_mode)
    dp.message.register(process_gregorian_date, BirthdayStates.waiting_for_gregorian_date)
    dp.message.register(process_hebrew_day, BirthdayStates.waiting_for_hebrew_day)
    dp.message.register(process_hebrew_month, BirthdayStates.waiting_for_hebrew_month)
    dp.message.register(process_hebrew_year, BirthdayStates.waiting_for_hebrew_year)
    dp.message.register(process_description, BirthdayStates.waiting_for_description)
    dp.message.register(process_notification_mode, BirthdayStates.waiting_for_notification_mode)
    dp.message.register(confirm_birthday, BirthdayStates.confirmation)