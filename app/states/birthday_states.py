from aiogram.fsm.state import StatesGroup, State

class BirthdayStates(StatesGroup):
    waiting_for_name = State()
    waiting_for_date = State()
    confirmation = State()