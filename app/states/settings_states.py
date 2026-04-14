from aiogram.fsm.state import State, StatesGroup


class SettingsStates(StatesGroup):
    waiting_for_notification_days = State()
    waiting_for_date_display_format = State()