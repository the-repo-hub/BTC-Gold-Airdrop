from aiogram.fsm.state import StatesGroup, State

class Checking(StatesGroup):
    twitter_waiting = State()
    instagram_waiting = State()
    email_waiting = State()
    wallet_waiting = State()


class Support(StatesGroup):
    problem_waiting = State()


class Referral(StatesGroup):
    wallet_waiting = State()