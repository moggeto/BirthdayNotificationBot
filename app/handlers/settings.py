from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext

from app.database.session import get_session
from app.keyboards.reply import (
    main_menu,
    settings_menu,
    notifications_settings_menu,
)
from app.services.notifications import get_notification_days, set_notification_days
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
        notify_before = get_notification_days(session, user, default=1)

    await state.set_state(SettingsStates.waiting_for_notification_days)
    await message.answer(
        "Настройки уведомлений.\n"
        f"Сейчас: за {notify_before} дн. до дня рождения.\n\n"
        "Введи новое количество дней.",
        reply_markup=notifications_settings_menu,
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
        notify_before = int(text)

        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )
            set_notification_days(session, user, notify_before)

        await state.clear()
        await message.answer(
            f"Готово. Уведомление будет приходить за {notify_before} дн. до дня рождения.",
            reply_markup=settings_menu,
        )

    except ValueError:
        await message.answer("Введи целое положительное число. Например: 3")


async def back_to_main_menu_from_settings(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer(
        "Возвращаю в главное меню.",
        reply_markup=main_menu,
    )


def register_settings_handlers(dp: Dispatcher):
    dp.message.register(show_settings, lambda message: message.text == "Настройки")
    dp.message.register(open_notifications_settings, lambda message: message.text == "Уведомления")
    dp.message.register(process_notification_days, SettingsStates.waiting_for_notification_days)
    dp.message.register(
        back_to_main_menu_from_settings,
        lambda message: message.text == "В главное меню",
    )