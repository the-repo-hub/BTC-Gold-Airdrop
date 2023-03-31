import sqlite3
from typing import Union
from aiogram import types
from aiogram.dispatcher.filters.state import StatesGroup, State


class Checking(StatesGroup):
    twitter_waiting = State()
    instagram_waiting = State()
    email_waiting = State()
    wallet_waiting = State()


class Support(StatesGroup):
    problem_waiting = State()


class Referral(StatesGroup):
    wallet_waiting = State()


class User:
    def __init__(self, line):
        self.pk, self.id, self.first_name, self.last_name, self.username, self.twitter_username, self.instagram_username,\
            self.email, self.wallet, self.referral_wallet, self.validated = line

    def get_profile_text(self):
        text = f"ID: {self.id}\n" \
               f"Name: {self.first_name}\n" \
               f"Username: {self.username}\n\n" \
               f"Twitter: {self.twitter_username}\n" \
               f"Instagram: {self.instagram_username}\n" \
               f"Email: {self.email}\n" \
               f"Referral wallet: {self.referral_wallet}\n" \
               f"Wallet address: {self.wallet}"
        return text


class Base(sqlite3.Connection):
    def __init__(self, base: str):
        super(Base, self).__init__(base)

    def create_user(self, m: Union[types.Message, types.CallbackQuery]) -> User:
        self.execute('insert into users values (NULL,?,?,?,?,NULL,NULL,NULL,NULL,NULL,0)',
                     (m.from_user.id, m.from_user.first_name, m.from_user.last_name, m.from_user.username))
        self.commit()
        return self.get_user_by_id(m.from_user.id)

    def get_user_by_id(self, user_id: int) -> Union[User, bool]:
        line = self.execute(f'select * from users where id={user_id}').fetchone()
        if line:
            return User(line)
        return False

    def user_decorator(self, fn):
        def inner(m: types.Message):
            if not self.get_user_by_id(m.from_user.id):
                self.create_user(m)
            return fn(m)
        return inner

    def get_all_fields_in_column(self, column: str):
        result = self.execute(f"select {column} from users").fetchall()
        return {result[0] for result in result}

    def set_user_field(self, user_id: int, field: str, content: Union[str, int]) -> str:
        self.execute(f"update users set '{field}' = '{content}' where id={user_id}")
        self.commit()
        return content

    def increase_int_field(self, user_id: int, field: str, num: int = 1):
        self.execute(f'update users set {field} = {field} + {num} where id={user_id}')
        self.commit()
        return num
