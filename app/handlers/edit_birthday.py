from aiogram import Dispatcher, types
from aiogram.types import CallbackQuery
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from app.database.session import get_session
from app.keyboards.edit_inline import (
    get_birthdays_for_edit_keyboard,
    get_birthday_actions_keyboard,
    get_edit_fields_keyboard,
    get_delete_confirmation_keyboard,
)
from app.keyboards.reply import main_menu, cancel_menu
from app.services.birthday_management import (
    get_birthdays_for_management,
    get_birthday_by_id_for_user,
    delete_birthday_by_id,
    update_birthday_name,
    update_birthday_date,
    update_birthday_year,
    update_birthday_description,
)
from app.services.users import get_or_create_user
from app.states.edit_birthday_states import EditBirthdayStates
from app.services.validators import validate_day_month
from app.services.date_formatting import format_full


def format_birthday_line(birthday, display_format):
    full_name = f"{birthday.first_name} {birthday.last_name}".strip()
    date_text = format_full(birthday, display_format)

    text = f"{full_name} — {date_text}"

    if birthday.description:
        text += f"\nОписание: {birthday.description}"

    return text


async def start_edit_birthday(message: types.Message):
    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=message.from_user.id,
            name=message.from_user.full_name,
        )
        birthdays = get_birthdays_for_management(session, user)
        display_format = user.date_display_format

    if not birthdays:
        await message.answer("У тебя нет записей для редактирования.")
        return

    await message.answer(
        "Выбери день рождения:",
        reply_markup=get_birthdays_for_edit_keyboard(birthdays, display_format),
    )


async def select_birthday_for_action(callback: CallbackQuery):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            name=callback.from_user.full_name,
        )
        birthday = get_birthday_by_id_for_user(session, user, birthday_id)
        display_format = user.date_display_format

    if not birthday:
        await callback.answer("Запись не найдена.")
        return

    await callback.message.edit_text(
        f"Что сделать с записью?\n{format_birthday_line(birthday, display_format)}",
        reply_markup=get_birthday_actions_keyboard(birthday.id),
    )
    await callback.answer()


async def choose_edit_action(callback: CallbackQuery):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            name=callback.from_user.full_name,
        )
        birthday = get_birthday_by_id_for_user(session, user, birthday_id)
        display_format = user.date_display_format

    if not birthday:
        await callback.answer("Запись не найдена.")
        return

    await callback.message.edit_text(
        f"Что именно изменить?\n{format_birthday_line(birthday, display_format)}",
        reply_markup=get_edit_fields_keyboard(birthday.id),
    )
    await callback.answer()


async def choose_delete_action(callback: CallbackQuery):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            name=callback.from_user.full_name,
        )
        birthday = get_birthday_by_id_for_user(session, user, birthday_id)
        display_format = user.date_display_format

    if not birthday:
        await callback.answer("Запись не найдена.")
        return

    await callback.message.edit_text(
        f"Удалить запись?\n{format_birthday_line(birthday, display_format)}",
        reply_markup=get_delete_confirmation_keyboard(birthday.id),
    )
    await callback.answer()


async def start_edit_name(callback: CallbackQuery, state: FSMContext):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    await state.update_data(edit_birthday_id=birthday_id)
    await state.set_state(EditBirthdayStates.waiting_for_new_name)

    await callback.message.answer(
        "Введи новое имя и фамилию:",
        reply_markup=cancel_menu,
    )
    await callback.answer()


async def start_edit_date(callback: CallbackQuery, state: FSMContext):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    await state.update_data(edit_birthday_id=birthday_id)
    await state.set_state(EditBirthdayStates.waiting_for_new_date)

    await callback.message.answer(
        "Введи новую дату в формате ДД.ММ:",
        reply_markup=cancel_menu,
    )
    await callback.answer()


async def start_edit_year(callback: CallbackQuery, state: FSMContext):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    await state.update_data(edit_birthday_id=birthday_id)
    await state.set_state(EditBirthdayStates.waiting_for_new_year)

    await callback.message.answer(
        "Введи новый год рождения.\n"
        "Если хочешь убрать год, отправь '-'",
        reply_markup=cancel_menu,
    )
    await callback.answer()


async def start_edit_description(callback: CallbackQuery, state: FSMContext):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    await state.update_data(edit_birthday_id=birthday_id)
    await state.set_state(EditBirthdayStates.waiting_for_new_description)

    await callback.message.answer(
        "Введи новое описание.\n"
        "Если хочешь очистить описание, отправь '-'",
        reply_markup=cancel_menu,
    )
    await callback.answer()


async def process_new_name(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.clear()
        await message.answer("Изменение отменено.", reply_markup=main_menu)
        return

    data = await state.get_data()
    birthday_id = data.get("edit_birthday_id")

    if not birthday_id:
        await state.clear()
        await message.answer("Не удалось определить запись.", reply_markup=main_menu)
        return

    try:
        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )
            birthday = update_birthday_name(session, user, birthday_id, message.text)
            display_format = user.date_display_format

        if not birthday:
            await message.answer("Запись не найдена.", reply_markup=main_menu)
            await state.clear()
            return

        await message.answer(
            f"Имя обновлено:\n{format_birthday_line(birthday, display_format)}",
            reply_markup=main_menu,
        )
        await state.clear()

    except ValueError as e:
        await message.answer(str(e))
    except IntegrityError:
        await message.answer("Такая запись уже существует.")
    except Exception as e:
        await message.answer(f"Ошибка при обновлении имени: {e}")


async def process_new_date(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.clear()
        await message.answer("Изменение отменено.", reply_markup=main_menu)
        return

    data = await state.get_data()
    birthday_id = data.get("edit_birthday_id")

    if not birthday_id:
        await state.clear()
        await message.answer("Не удалось определить запись.", reply_markup=main_menu)
        return

    try:
        day, month = map(int, message.text.split("."))
        validate_day_month(day, month)

        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )
            birthday = update_birthday_date(session, user, birthday_id, day, month)
            display_format = user.date_display_format

        if not birthday:
            await message.answer("Запись не найдена.", reply_markup=main_menu)
            await state.clear()
            return

        await message.answer(
            f"Дата обновлена:\n{format_birthday_line(birthday, display_format)}",
            reply_markup=main_menu,
        )
        await state.clear()

    except ValueError as e:
        await message.answer(str(e))
    except IntegrityError:
        await message.answer("Такая запись уже существует.")


async def process_new_year(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.clear()
        await message.answer("Изменение отменено.", reply_markup=main_menu)
        return

    data = await state.get_data()
    birthday_id = data.get("edit_birthday_id")

    if not birthday_id:
        await state.clear()
        await message.answer("Не удалось определить запись.", reply_markup=main_menu)
        return

    text = (message.text or "").strip()

    try:
        year = None if text == "-" else int(text)

        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )
            birthday = update_birthday_year(session, user, birthday_id, year)
            display_format = user.date_display_format

        if not birthday:
            await message.answer("Запись не найдена.", reply_markup=main_menu)
            await state.clear()
            return

        await message.answer(
            f"Год обновлён:\n{format_birthday_line(birthday, display_format)}",
            reply_markup=main_menu,
        )
        await state.clear()

    except ValueError as e:
        await message.answer(str(e))
    except IntegrityError:
        await message.answer("Такая запись уже существует.")


async def process_new_description(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await state.clear()
        await message.answer("Изменение отменено.", reply_markup=main_menu)
        return

    data = await state.get_data()
    birthday_id = data.get("edit_birthday_id")

    if not birthday_id:
        await state.clear()
        await message.answer("Не удалось определить запись.", reply_markup=main_menu)
        return

    text = (message.text or "").strip()
    description = "" if text == "-" else text

    try:
        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )
            birthday = update_birthday_description(session, user, birthday_id, description)
            display_format = user.date_display_format

        if not birthday:
            await message.answer("Запись не найдена.", reply_markup=main_menu)
            await state.clear()
            return

        await message.answer(
            f"Описание обновлено:\n{format_birthday_line(birthday, display_format)}",
            reply_markup=main_menu,
        )
        await state.clear()

    except Exception as e:
        await message.answer(f"Ошибка при обновлении описания: {e}")


async def confirm_delete_birthday(callback: CallbackQuery):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            name=callback.from_user.full_name,
        )
        birthday = get_birthday_by_id_for_user(session, user, birthday_id)
        display_format = user.date_display_format

        if not birthday:
            await callback.answer("Запись уже удалена или не найдена.")
            return

        deleted_text = format_birthday_line(birthday, display_format)
        delete_birthday_by_id(session, user, birthday_id)

    await callback.message.edit_text(f"Удалено:\n{deleted_text}")
    await callback.answer("Запись удалена.")


async def back_to_actions(callback: CallbackQuery):
    try:
        birthday_id = int(callback.data.split(":")[1])
    except (IndexError, ValueError):
        await callback.answer("Некорректный запрос.")
        return

    with get_session() as session:
        user = get_or_create_user(
            session=session,
            telegram_id=callback.from_user.id,
            name=callback.from_user.full_name,
        )
        birthday = get_birthday_by_id_for_user(session, user, birthday_id)
        display_format = user.date_display_format

    if not birthday:
        await callback.answer("Запись не найдена.")
        return

    await callback.message.edit_text(
        f"Что сделать с записью?\n{format_birthday_line(birthday, display_format)}",
        reply_markup=get_birthday_actions_keyboard(birthday.id),
    )
    await callback.answer()


async def cancel_edit_birthday(callback: CallbackQuery):
    await callback.message.edit_text("Действие отменено.")
    await callback.answer()


def register_edit_handlers(dp: Dispatcher):
    dp.message.register(
        start_edit_birthday,
        lambda message: message.text == "Редактировать день рождения",
    )
    dp.callback_query.register(
        select_birthday_for_action,
        lambda c: c.data.startswith("edit_birthday_select:"),
    )
    dp.callback_query.register(
        choose_edit_action,
        lambda c: c.data.startswith("edit_birthday_action_edit:"),
    )
    dp.callback_query.register(
        choose_delete_action,
        lambda c: c.data.startswith("edit_birthday_action_delete:"),
    )
    dp.callback_query.register(
        start_edit_name,
        lambda c: c.data.startswith("edit_birthday_field_name:"),
    )
    dp.callback_query.register(
        start_edit_date,
        lambda c: c.data.startswith("edit_birthday_field_date:"),
    )
    dp.callback_query.register(
        start_edit_year,
        lambda c: c.data.startswith("edit_birthday_field_year:"),
    )
    dp.callback_query.register(
        start_edit_description,
        lambda c: c.data.startswith("edit_birthday_field_description:"),
    )
    dp.message.register(process_new_name, EditBirthdayStates.waiting_for_new_name)
    dp.message.register(process_new_date, EditBirthdayStates.waiting_for_new_date)
    dp.message.register(process_new_year, EditBirthdayStates.waiting_for_new_year)
    dp.message.register(process_new_description, EditBirthdayStates.waiting_for_new_description)
    dp.callback_query.register(
        confirm_delete_birthday,
        lambda c: c.data.startswith("edit_birthday_confirm_delete:"),
    )
    dp.callback_query.register(
        back_to_actions,
        lambda c: c.data.startswith("edit_birthday_back_to_actions:"),
    )
    dp.callback_query.register(
        cancel_edit_birthday,
        lambda c: c.data == "edit_birthday_cancel",
    )