from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext

from app.database.session import get_session
from app.keyboards.reply import main_menu, confirm_menu, cancel_menu
from app.services.birthdays import create_birthday
from app.services.users import get_or_create_user
from app.states.birthday_states import BirthdayStates


async def start_adding_birthday(message: types.Message, state: FSMContext):
    await message.answer("Пожалуйста, введите имя и фамилию:", reply_markup=cancel_menu)
    await state.set_state(BirthdayStates.waiting_for_name)


async def process_name(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await cancel_operation(message, state)
        return

    if not message.text or not message.text.strip():
        await message.answer("Имя не может быть пустым. Введите имя ещё раз.")
        return

    await state.update_data(name=message.text.strip())
    await message.answer("Теперь введите дату рождения в формате ДД.ММ:", reply_markup=cancel_menu)
    await state.set_state(BirthdayStates.waiting_for_date)


async def process_date(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await cancel_operation(message, state)
        return

    try:
        day, month = map(int, message.text.split("."))

        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError

        await state.update_data(day=day, month=month)
        await message.answer(
            "Введите год рождения (опционально). Если не хотите указывать — отправьте любой текст, например '-'",
            reply_markup=cancel_menu,
        )
        await state.set_state(BirthdayStates.waiting_for_year)

    except ValueError:
        await message.answer("Неверный формат даты. Введите ещё раз в формате ДД.ММ.")


async def process_year(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await cancel_operation(message, state)
        return

    text = (message.text or "").strip()

    if text.isdigit():
        year = int(text)
        if year <= 0:
            await message.answer("Год должен быть положительным числом. Введите год ещё раз или пропустите шаг.")
            return
        await state.update_data(year=year)
    else:
        await state.update_data(year=None)

    data = await state.get_data()
    year_info = data["year"] if data.get("year") else "не указан"

    await message.answer(
        f"Проверьте данные:\n"
        f"Имя и фамилия: {data['name']}\n"
        f"Дата рождения: {data['day']:02}.{data['month']:02}\n"
        f"Год рождения: {year_info}",
        reply_markup=confirm_menu,
    )
    await state.set_state(BirthdayStates.confirmation)


async def confirm_birthday(message: types.Message, state: FSMContext):
    if message.text == "Назад":
        await cancel_operation(message, state)
        return

    if message.text != "Подтвердить":
        await message.answer("Пожалуйста, выберите одну из опций: Подтвердить или Назад.")
        return

    data = await state.get_data()

    try:
        with get_session() as session:
            user = get_or_create_user(
                session=session,
                telegram_id=message.from_user.id,
                name=message.from_user.full_name,
            )

            birthday = create_birthday(
                session=session,
                user=user,
                full_name=data["name"],
                day=data["day"],
                month=data["month"],
                year=data.get("year"),
            )

        full_name = f"{birthday.first_name} {birthday.last_name}".strip()
        await message.answer(
            f"День рождения {full_name} успешно добавлен!",
            reply_markup=main_menu,
        )
        await state.clear()

    except ValueError as e:
        await message.answer(str(e))
    except Exception as e:
        await message.answer(f"Ошибка при добавлении: {e}")


async def cancel_operation(message: types.Message, state: FSMContext):
    await state.clear()
    await message.answer("Операция отменена. Возвращаю вас в главное меню.", reply_markup=main_menu)


def register_add_handlers(dp: Dispatcher):
    dp.message.register(start_adding_birthday, lambda message: message.text == "Добавить день рождения")
    dp.message.register(process_name, BirthdayStates.waiting_for_name)
    dp.message.register(process_date, BirthdayStates.waiting_for_date)
    dp.message.register(process_year, BirthdayStates.waiting_for_year)
    dp.message.register(confirm_birthday, BirthdayStates.confirmation)