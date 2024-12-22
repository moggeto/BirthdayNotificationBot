from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить день рождения'),
            KeyboardButton(text='Редактировать день рождения'),
            KeyboardButton(text='Просмотр дней рождений')],

        [
            KeyboardButton(text='Настройки')
        ]

    ],
    resize_keyboard=True
)

confirm_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Подтвердить"), KeyboardButton(text="Назад")]
    ], resize_keyboard=True
)

cancel_menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Назад")]
    ], resize_keyboard=True
)


