from aiogram.types import ReplyKeyboardMarkup, KeyboardButton


main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Добавить день рождения")],
        [KeyboardButton(text="Просмотр дней рождений")],
        [KeyboardButton(text="Редактировать день рождения")],
        [KeyboardButton(text="Настройки")],
    ],
    resize_keyboard=True,
)

confirm_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подтвердить")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)

cancel_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)

settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Уведомления")],
        [KeyboardButton(text="Формат отображения дат")],
        [KeyboardButton(text="В главное меню")],
    ],
    resize_keyboard=True,
)

notifications_settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад")],
        [KeyboardButton(text="В главное меню")],
    ],
    resize_keyboard=True,
)

date_display_settings_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Только григорианская")],
        [KeyboardButton(text="Только еврейская")],
        [KeyboardButton(text="Обе даты")],
        [KeyboardButton(text="Назад")],
        [KeyboardButton(text="В главное меню")],
    ],
    resize_keyboard=True,
)

date_type_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Только григорианская")],
        [KeyboardButton(text="Только еврейская")],
        [KeyboardButton(text="Обе даты")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)

both_date_mode_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Автоконвертация из григорианской")],
        [KeyboardButton(text="Ввести еврейскую вручную")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)

notification_mode_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Напоминать по григорианской")],
        [KeyboardButton(text="Напоминать по еврейской")],
        [KeyboardButton(text="Напоминать по обеим")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)

hebrew_months_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Тишрей"), KeyboardButton(text="Хешван")],
        [KeyboardButton(text="Кислев"), KeyboardButton(text="Тевет")],
        [KeyboardButton(text="Шват"), KeyboardButton(text="Адар")],
        [KeyboardButton(text="Адар I"), KeyboardButton(text="Адар II")],
        [KeyboardButton(text="Нисан"), KeyboardButton(text="Ияр")],
        [KeyboardButton(text="Сиван"), KeyboardButton(text="Таммуз")],
        [KeyboardButton(text="Ав"), KeyboardButton(text="Элул")],
        [KeyboardButton(text="Назад")],
    ],
    resize_keyboard=True,
)