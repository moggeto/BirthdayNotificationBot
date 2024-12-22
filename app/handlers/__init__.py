from aiogram import Dispatcher
from app.handlers.commands import register_command_handlers
from app.handlers.view_birthday import register_view_handlers
from app.handlers.notify import register_notify_handlers
# from app.handlers.buttons import register_text_handlers
from app.handlers.add_date import register_add_handlers



def register_handlers(dp: Dispatcher):
    """
    Регистрирует все хендлеры из различных модулей.
    """
    register_add_handlers(dp)
    register_view_handlers(dp)
    register_command_handlers(dp)
    register_notify_handlers(dp)
    # register_text_handlers(dp)

