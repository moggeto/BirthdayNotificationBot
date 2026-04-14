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