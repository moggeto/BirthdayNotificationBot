# from aiogram import types, Dispatcher
# from aiogram.fsm.context import FSMContext
# from app.database.session import Session
# from app.database.models import Birthday
# from app.keyboards.reply import main_menu, confirm_menu, cancel_menu
# from app.states.birthday_states import BirthdayStates
#
#
# async def start_adding_birthday(message: types.Message, state: FSMContext):
#     """
#     Начало процесса добавления дня рождения.
#     """
#     await message.answer("Пожалуйста, введите имя и фамилию:", reply_markup=cancel_menu)
#     await state.set_state(BirthdayStates.waiting_for_name)
#
#
# async def process_name(message: types.Message, state: FSMContext):
#     """
#     Обрабатывает введённое имя и фамилию.
#     """
#     if message.text == "Назад":
#         await cancel_operation(message, state)
#         return
#
#     await state.update_data(name=message.text)
#     await message.answer("Теперь введите дату рождения в формате ДД.ММ:", reply_markup=cancel_menu)
#     await state.set_state(BirthdayStates.waiting_for_date)
#
#
# async def process_date(message: types.Message, state: FSMContext):
#     """
#     Обрабатывает введённую дату рождения.
#     """
#     if message.text == "Назад":
#         await cancel_operation(message, state)
#         return
#
#     try:
#         day, month = map(int, message.text.split("."))
#         if not (1 <= day <= 31 and 1 <= month <= 12):
#             raise ValueError("Неверный формат даты.")
#         await state.update_data(day=day, month=month)
#         data = await state.get_data()
#         await message.answer(
#             f"Проверьте данные:\n"
#             f"Имя и фамилия: {data['name']}\n"
#             f"Дата рождения: {day:02}.{month:02}\n",
#             reply_markup=confirm_menu
#         )
#         await state.set_state(BirthdayStates.confirmation)
#     except ValueError:
#         await message.answer("Неверный формат даты. Введите ещё раз (ДД.ММ):")
#
#
# async def confirm_birthday(message: types.Message, state: FSMContext):
#     """
#     Подтверждение добавления дня рождения.
#     """
#     if message.text == "Назад":
#         await cancel_operation(message, state)
#         return
#
#     if message.text == "Подтвердить":
#         data = await state.get_data()
#         name, day, month = data['name'], data['day'], data['month']
#         first_name, last_name = name.split(maxsplit=1)
#         session = Session()
#         try:
#             new_birthday = Birthday(
#                 user_id=message.from_user.id,
#                 first_name=first_name,
#                 last_name=last_name,
#                 day=day,
#                 month=month
#             )
#             session.add(new_birthday)
#             session.commit()
#             await message.answer(f"День рождения {first_name} {last_name} успешно добавлен!", reply_markup=main_menu)
#         except Exception as e:
#             await message.answer(f"Ошибка при добавлении: {e}")
#         finally:
#             session.close()
#         await state.clear()
#     elif message.text == "Назад":
#         await message.answer("Добавление отменено.", reply_markup=types.ReplyKeyboardRemove())
#         await state.clear()
#     else:
#         await message.answer("Пожалуйста, выберите одну из опций: Подтвердить или Назад.")
#
#
# async def cancel_operation(message: types.Message, state: FSMContext):
#     """
#     Отмена текущей операции и выход из состояния.
#     """
#     await state.clear()
#     await message.answer("Операция отменена. Возвращаю вас в главное меню.", reply_markup=main_menu)
#
#
# def register_add_handlers(dp: Dispatcher):
#     """
#     Регистрирует все хендлеры для работы с Добавлением.
#     """
#     dp.message.register(start_adding_birthday, lambda message: message.text == "Добавить день рождения")
#     dp.message.register(process_name, BirthdayStates.waiting_for_name)
#     dp.message.register(process_date, BirthdayStates.waiting_for_date)
#     dp.message.register(confirm_birthday, BirthdayStates.confirmation)
from aiogram import types, Dispatcher
from aiogram.fsm.context import FSMContext
from app.database.session import Session
from app.database.models import Birthday
from app.keyboards.reply import main_menu, confirm_menu, cancel_menu
from app.states.birthday_states import BirthdayStates


async def start_adding_birthday(message: types.Message, state: FSMContext):
    """
    Начало процесса добавления дня рождения.
    """
    await message.answer("Пожалуйста, введите имя и фамилию:", reply_markup=cancel_menu)
    await state.set_state(BirthdayStates.waiting_for_name)


async def process_name(message: types.Message, state: FSMContext):
    """
    Обрабатывает введённое имя и фамилию.
    """
    if message.text == "Назад":
        await cancel_operation(message, state)
        return

    await state.update_data(name=message.text)
    await message.answer("Теперь введите дату рождения в формате ДД.ММ:", reply_markup=cancel_menu)
    await state.set_state(BirthdayStates.waiting_for_date)


async def process_date(message: types.Message, state: FSMContext):
    """
    Обрабатывает введённую дату рождения.
    """
    if message.text == "Назад":
        await cancel_operation(message, state)
        return

    try:
        day, month = map(int, message.text.split("."))
        if not (1 <= day <= 31 and 1 <= month <= 12):
            raise ValueError("Неверный формат даты.")
        await state.update_data(day=day, month=month)
        await message.answer(
            "Введите год рождения (опционально). Если вы не знаете год, просто пропустите этот шаг.",
            reply_markup=cancel_menu
        )
        await state.set_state(BirthdayStates.waiting_for_year)
    except ValueError:
        await message.answer("Неверный формат даты. Введите ещё раз (ДД.ММ):")


# async def process_year(message: types.Message, state: FSMContext):
#     """
#     Обрабатывает введённый год рождения (опционально).
#     """
#     if message.text == "Назад":
#         await cancel_operation(message, state)
#         return
#
#     if message.text.isdigit():
#         year = int(message.text)
#         if year < 1900 or year > 2100:
#             await message.answer("Введите корректный год (между 1900 и 2100) или пропустите этот шаг.")
#             return
#         await state.update_data(year=year)
#     else:
#         await state.update_data(year=None)
#
#     data = await state.get_data()
#     year_info = f"{data['year']}" if data['year'] else "не указан"
#     await message.answer(
#         f"Проверьте данные:\n"
#         f"Имя и фамилия: {data['name']}\n"
#         f"Дата рождения: {data['day']:02}.{data['month']:02}\n"
#         f"Год рождения: {year_info}",
#         reply_markup=confirm_menu
#     )
#     await state.set_state(BirthdayStates.confirmation)


async def process_year(message: types.Message, state: FSMContext):
    """
    Обрабатывает введённый год рождения (опционально).
    """
    if message.text == "Назад":
        await cancel_operation(message, state)
        return

    if message.text.isdigit():
        year = int(message.text)
        if year <= 0:
            await message.answer("Год должен быть положительным числом. Введите год ещё раз или пропустите этот шаг.")
            return
        await state.update_data(year=year)
    else:
        await state.update_data(year=None)

    data = await state.get_data()
    year_info = f"{data['year']}" if data['year'] else "не указан"
    await message.answer(
        f"Проверьте данные:\n"
        f"Имя и фамилия: {data['name']}\n"
        f"Дата рождения: {data['day']:02}.{data['month']:02}\n"
        f"Год рождения: {year_info}",
        reply_markup=confirm_menu
    )
    await state.set_state(BirthdayStates.confirmation)


async def confirm_birthday(message: types.Message, state: FSMContext):
    """
    Подтверждение добавления дня рождения.
    """
    if message.text == "Назад":
        await cancel_operation(message, state)
        return

    if message.text == "Подтвердить":
        data = await state.get_data()
        name, day, month, year = data['name'], data['day'], data['month'], data.get('year')
        first_name, last_name = name.split(maxsplit=1)
        session = Session()
        try:
            new_birthday = Birthday(
                user_id=message.from_user.id,
                first_name=first_name,
                last_name=last_name,
                day=day,
                month=month,
                year=year
            )
            session.add(new_birthday)
            session.commit()
            await message.answer(f"День рождения {first_name} {last_name} успешно добавлен!", reply_markup=main_menu)
        except Exception as e:
            await message.answer(f"Ошибка при добавлении: {e}")
        finally:
            session.close()
        await state.clear()
    elif message.text == "Назад":
        await message.answer("Добавление отменено.", reply_markup=types.ReplyKeyboardRemove())
        await state.clear()
    else:
        await message.answer("Пожалуйста, выберите одну из опций: Подтвердить или Назад.")


async def cancel_operation(message: types.Message, state: FSMContext):
    """
    Отмена текущей операции и выход из состояния.
    """
    await state.clear()
    await message.answer("Операция отменена. Возвращаю вас в главное меню.", reply_markup=main_menu)


def register_add_handlers(dp: Dispatcher):
    """
    Регистрирует все хендлеры для работы с Добавлением.
    """
    dp.message.register(start_adding_birthday, lambda message: message.text == "Добавить день рождения")
    dp.message.register(process_name, BirthdayStates.waiting_for_name)
    dp.message.register(process_date, BirthdayStates.waiting_for_date)
    dp.message.register(process_year, BirthdayStates.waiting_for_year)  # Новый шаг
    dp.message.register(confirm_birthday, BirthdayStates.confirmation)