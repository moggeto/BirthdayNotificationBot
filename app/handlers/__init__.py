from aiogram import Dispatcher
from app.handlers.crud import register_crud_handlers
from app.handlers.notify import register_notify_handlers


def register_handlers(dp: Dispatcher):
    """
    Регистрирует все хендлеры из различных модулей.
    """
    register_crud_handlers(dp)
    register_notify_handlers(dp)