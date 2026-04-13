from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_birthdays_for_edit_keyboard(birthdays: list) -> InlineKeyboardMarkup:
    buttons = []

    for birthday in birthdays:
        full_name = f"{birthday.first_name} {birthday.last_name}".strip()
        text = f"{full_name} — {birthday.day:02}.{birthday.month:02}"
        if birthday.year:
            text += f".{birthday.year}"

        buttons.append([
            InlineKeyboardButton(
                text=text,
                callback_data=f"edit_birthday_select:{birthday.id}",
            )
        ])

    buttons.append([
        InlineKeyboardButton(
            text="Отмена",
            callback_data="edit_birthday_cancel",
        )
    ])

    return InlineKeyboardMarkup(inline_keyboard=buttons)


def get_birthday_actions_keyboard(birthday_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить",
                    callback_data=f"edit_birthday_action_edit:{birthday_id}",
                ),
                InlineKeyboardButton(
                    text="Удалить",
                    callback_data=f"edit_birthday_action_delete:{birthday_id}",
                ),
            ],
            [
                InlineKeyboardButton(
                    text="Отмена",
                    callback_data="edit_birthday_cancel",
                )
            ],
        ]
    )


def get_edit_fields_keyboard(birthday_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Изменить имя",
                    callback_data=f"edit_birthday_field_name:{birthday_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить дату",
                    callback_data=f"edit_birthday_field_date:{birthday_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Изменить год",
                    callback_data=f"edit_birthday_field_year:{birthday_id}",
                )
            ],
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=f"edit_birthday_back_to_actions:{birthday_id}",
                )
            ],
        ]
    )


def get_delete_confirmation_keyboard(birthday_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Да, удалить",
                    callback_data=f"edit_birthday_confirm_delete:{birthday_id}",
                ),
                InlineKeyboardButton(
                    text="Нет",
                    callback_data=f"edit_birthday_back_to_actions:{birthday_id}",
                ),
            ]
        ]
    )