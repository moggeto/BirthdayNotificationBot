from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext

from app.database.models import DateDisplayFormat
from app.database.session import get_session
from app.keyboards.reply import (
    main_menu,
    settings_menu,
    notifications_settings_menu,
    date_display_settings_menu,
)
from app.services.notifications import (
    get_notification_days_list,
    add_notification_day,
    remove_notification_day,
    format_notification_days,
)
from app.services.date_display import (
    get_date_display_format,
    set_date_display_format,
    format_date_display_label,
)
from app.services.users import get_or_create_user
from app.states.settings_states import SettingsStates


async def show_settings(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Настройки.\nВыбери раздел:",
        reply_markup=settings_menu,
    )


async def open_notifications_settings(message: types.Message, state: FSMContext):
    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
        )
        days_list = get_notification_days_list(session, user, default=[1])

    await state.set_state(SettingsStates.waiting_for_notification_days)
    await message.answer(
        "Настройки уведомлений.\n"
        f"Сейчас: {format_notification_days(days_list)} дн. до дня рождения.\n\n"
        "Введи число, чтобы ДОБАВИТЬ уведомление.\n"
        "Введи число с минусом, чтобы УДАЛИТЬ уведомление.\n\n"
        "Примеры:\n"
        "7  -> добавить уведомление за 7 дней\n"
        "-7 -> удалить уведомление за 7 дней",
        reply_markup=notifications_settings_menu,
    )


async def open_date_display_settings(message: types.Message, state: FSMContext):
    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
        )
        current_format = get_date_display_format(session, user)

    await state.set_state(SettingsStates.waiting_for_date_display_format)
    await message.answer(
        "Формат отображения дат.\n"
        f"Сейчас: {format_date_display_label(current_format)}.\n\n"
        "Выбери, как показывать даты в карточках и списках.",
        reply_markup=date_display_settings_menu,
    )


async def process_notification_days(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await state.clear()
        await message.answer(
            "Настройки.\nВыбери раздел:",
            reply_markup=settings_menu,
        )
        return

    if text == "В главное меню":
        await state.clear()
        await message.answer(
            "Возвращаю в главное меню.",
            reply_markup=main_menu,
        )
        return

    try:
        value = int(text)

        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )

            if value > 0:
                add_notification_day(session, user, value)
                action_text = f"Добавлено уведомление за {value} дн."
            elif value < 0:
                days_to_remove = abs(value)
                removed = remove_notification_day(session, user, days_to_remove)
                if not removed:
                    await message.answer(
                        f"Уведомление за {days_to_remove} дн. не найдено.",
                        reply_markup=notifications_settings_menu,
                    )
                    return
                action_text = f"Удалено уведомление за {days_to_remove} дн."
            else:
                await message.answer("0 нельзя использовать. Введи число больше 0 или отрицательное для удаления.")
                return

            updated_days = get_notification_days_list(session, user, default=[])

        await message.answer(
            f"{action_text}\n"
            f"Теперь установлено: {format_notification_days(updated_days)} дн.",
            reply_markup=notifications_settings_menu,
        )

    except ValueError as e:
        text_error = str(e)
        if text_error:
            await message.answer(text_error)
        else:
            await message.answer("Введи целое число. Например: 7 или -7")


async def process_date_display_format(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await state.clear()
        await message.answer(
            "Настройки.\nВыбери раздел:",
            reply_markup=settings_menu,
        )
        return

    if text == "В главное меню":
        await state.clear()
        await message.answer(
            "Возвращаю в главное меню.",
            reply_markup=main_menu,
        )
        return

    mapping = {
        "Только григорианская": DateDisplayFormat.gregorian,
        "Только еврейская": DateDisplayFormat.hebrew,
        "Обе даты": DateDisplayFormat.both,
    }

    selected_value = mapping.get(text)
    if not selected_value:
        await message.answer(
            "Выбери один из готовых вариантов кнопками.",
            reply_markup=date_display_settings_menu,
        )
        return

    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
        )
        updated_value = set_date_display_format(session, user, selected_value)

    await message.answer(
        f"Сохранено.\nТеперь формат отображения: {format_date_display_label(updated_value)}.",
        reply_markup=date_display_settings_menu,
    )


async def back_to_main_menu_from_settings(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Возвращаю в главное меню.",
        reply_markup=main_menu,
    )


def register_settings_handlers(dp: Dispatcher):
    dp.message.register(show_settings, lambda message: message.text == "Настройки")
    dp.message.register(open_notifications_settings, lambda message: message.text == "Уведомления")
    dp.message.register(
        open_date_display_settings,
        lambda message: message.text == "Формат отображения дат",
    )

    dp.message.register(process_notification_days, SettingsStates.waiting_for_notification_days)
    dp.message.register(process_date_display_format, SettingsStates.waiting_for_date_display_format)

    dp.message.register(
        back_to_main_menu_from_settings,
        lambda message: message.text == "В главное меню",
    )