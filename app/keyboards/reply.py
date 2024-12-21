from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

main_menu = ReplyKeyboardMarkup(
    keyboard=[
        [
            KeyboardButton(text='Добавить день рождения'),
            KeyboardButton(text='Редактировать день рождения'),
            KeyboardButton(text='Список дней рождений')],

        [
            KeyboardButton(text='Настройки')
        ]

    ],
    resize_keyboard=True
)
