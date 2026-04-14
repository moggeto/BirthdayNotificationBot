from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from sqlalchemy.exc import IntegrityError

from app.database.session import get_session
from app.keyboards.reply import main_menu, confirm_menu, cancel_menu
from app.services.birthdays import create_birthday
from app.services.users import get_or_create_user
from app.states.birthday_states import BirthdayStates
from app.services.validators import parse_date_with_optional_year
from sqlalchemy.orm import selectinload
from app.database.models import Birthday
from app.services.date_formatting import format_full


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
        "Теперь введите дату рождения.\n"
        "Форматы:\n"
        "ДД.ММ — если без года\n"
        "ДД.ММ.ГГГГ — если с годом",
        reply_markup=cancel_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_date)


async def process_date(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await cancel_operation(message, state)
        return

    try:
        day, month, year = parse_date_with_optional_year(text)
    except ValueError as e:
        await message.answer(str(e))
        return

    await state.update_data(day=day, month=month, year=year)
    await message.answer(
        "Теперь введите описание или заметку.\n"
        "Например: что любит, идеи для подарка и т.д.\n"
        "Если описание не нужно — отправьте '-'",
        reply_markup=cancel_menu,
    )
    await state.set_state(BirthdayStates.waiting_for_description)


async def process_description(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await cancel_operation(message, state)
        return

    description = "" if text == "-" else text
    await state.update_data(description=description)

    data = await state.get_data()

    date_text = f"{data['day']:02}.{data['month']:02}"
    if data.get("year"):
        date_text += f".{data['year']}"

    description_text = data["description"] if data.get("description") else "не указано"

    await message.answer(
        "Проверьте данные:\n"
        f"Имя и фамилия: {data['name']}\n"
        f"Дата рождения: {date_text}\n"
        f"Описание: {description_text}",
        reply_markup=confirm_menu,
    )
    await state.set_state(BirthdayStates.confirmation)


async def confirm_birthday(message: types.Message, state: FSMContext):
    text = (message.text or "").strip()

    if text == "Назад":
        await cancel_operation(message, state)
        return

    if text != "Подтвердить":
        await message.answer("Нажмите «Подтвердить» или «Назад».")
        return

    data = await state.get_data()

    try:
        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )

            created_birthday = create_birthday(
                session=session,
                user=user,
                full_name=data["name"],
                day=data["day"],
                month=data["month"],
                year=data.get("year"),
                description=data.get("description", ""),
            )

            birthday = (
                session.query(Birthday)
                .options(selectinload(Birthday.dates))
                .filter(Birthday.id == created_birthday.id)
                .first()
            )

            if not birthday:
                raise ValueError("Не удалось загрузить созданную запись.")

            full_name = f"{birthday.first_name} {birthday.last_name}".strip()
            date_text = format_full(birthday, user.date_display_format)

        await message.answer(
            f"Добавлено:\n{full_name}\nДата: {date_text}",
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
    dp.message.register(process_date, BirthdayStates.waiting_for_date)
    dp.message.register(process_description, BirthdayStates.waiting_for_description)
    dp.message.register(confirm_birthday, BirthdayStates.confirmation)