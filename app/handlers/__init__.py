from aiogram import Dispatcher

from app.handlers.add_date import register_add_handlers
from app.handlers.commands import register_command_handlers
from app.handlers.edit_birthday import register_edit_handlers
from app.handlers.settings import register_settings_handlers
from app.handlers.view_birthday import register_view_handlers


def register_handlers(dp: Dispatcher):
    register_add_handlers(dp)
    register_view_handlers(dp)
    register_edit_handlers(dp)
    register_command_handlers(dp)
    register_settings_handlers(dp)