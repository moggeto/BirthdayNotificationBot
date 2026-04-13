from aiogram.fsm.state import State, StatesGroup


class EditBirthdayStates(StatesGroup):
    waiting_for_new_name = State()
    waiting_for_new_date = State()
    waiting_for_new_year = State()