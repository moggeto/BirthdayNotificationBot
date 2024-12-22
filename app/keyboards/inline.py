# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#
# def get_pagination_keyboard(page: int, total_pages: int, sort_by: str):
#     keyboard = InlineKeyboardMarkup(row_width=3)
#     if page > 1:
#         keyboard.add(InlineKeyboardButton("⬅️ Назад", callback_data=f"pagination:{page - 1}:{sort_by}"))
#     if page < total_pages:
#         keyboard.add(InlineKeyboardButton("Вперед ➡️", callback_data=f"pagination:{page + 1}:{sort_by}"))
#
#     keyboard.row(
#         InlineKeyboardButton("Сортировать по имени", callback_data="sort:name"),
#         InlineKeyboardButton("Сортировать по дате", callback_data="sort:date"),
#     )
#     keyboard.add(InlineKeyboardButton("🔙 Назад", callback_data="pagination:back"))
#     return keyboard
# from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
#
#
# def get_pagination_keyboard(page, total_pages, sort_by):
#     """
#     Возвращает клавиатуру для пагинации.
#     """
#     keyboard = []
#
#     # Кнопки сортировки
#     sort_buttons = [
#         InlineKeyboardButton("По имени", callback_data=f"sort:name"),
#         InlineKeyboardButton("По дате", callback_data=f"sort:date"),
#     ]
#     keyboard.append(sort_buttons)
#
#     # Кнопки пагинации
#     pagination_buttons = []
#     if page > 1:
#         pagination_buttons.append(InlineKeyboardButton("« Назад", callback_data=f"pagination:{page - 1}:{sort_by}"))
#     if page < total_pages:
#         pagination_buttons.append(InlineKeyboardButton("Вперед »", callback_data=f"pagination:{page + 1}:{sort_by}"))
#
#     if pagination_buttons:
#         keyboard.append(pagination_buttons)
#
#     return InlineKeyboardMarkup(inline_keyboard=keyboard)
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton


def get_pagination_keyboard(page, total_pages, sort_by):
    """
    Возвращает клавиатуру для пагинации.
    """
    keyboard = []

    # Кнопки сортировки
    sort_buttons = [
        InlineKeyboardButton(text="По имени", callback_data=f"sort:name"),
        InlineKeyboardButton(text="По дате", callback_data=f"sort:date"),
    ]
    keyboard.append(sort_buttons)

    # Кнопки пагинации
    pagination_buttons = []
    if page > 1:
        pagination_buttons.append(
            InlineKeyboardButton(text="« Назад", callback_data=f"pagination:{page - 1}:{sort_by}"))
    if page < total_pages:
        pagination_buttons.append(
            InlineKeyboardButton(text="Вперед »", callback_data=f"pagination:{page + 1}:{sort_by}"))

    if pagination_buttons:
        keyboard.append(pagination_buttons)

    return InlineKeyboardMarkup(inline_keyboard=keyboard)
