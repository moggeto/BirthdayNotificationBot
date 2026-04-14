from aiogram.fsm.state import State, StatesGroup


class BirthdayStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_date_type = State()
    waiting_for_both_mode = State()

    waiting_for_gregorian_date = State()

    waiting_for_hebrew_day = State()
    waiting_for_hebrew_month = State()
    waiting_for_hebrew_year = State()

    waiting_for_description = State()
    waiting_for_notification_mode = State()
    confirmation = State()