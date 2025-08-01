from aiogram.fsm.state import StatesGroup, State


class UserStates(StatesGroup):
    fill_supply = State()
    fill_price_from = State()
    fill_price_to = State()
    fill_channel = State()

    fill_stars = State()