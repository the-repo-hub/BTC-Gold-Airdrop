from functools import cached_property

from aiogram import types
from configs_processor import Config


class Keyboards:

    @cached_property
    def start_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add(Config.buttons.join)
        keyboard.add(Config.buttons.profile)
        keyboard.add(Config.buttons.support)
        keyboard.add(Config.buttons.cancel)
        return keyboard

    @cached_property
    def submit_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add(Config.buttons.submit_details)
        keyboard.add(Config.buttons.specify_referral)
        keyboard.add(Config.buttons.back)
        keyboard.add(Config.buttons.support)
        return keyboard

    @cached_property
    def cancel_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add(Config.buttons.cancel)
        return keyboard

    @cached_property
    def profile_keyboard(self):
        keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
        keyboard.add(Config.buttons.join)
        keyboard.add(Config.buttons.back)
        return keyboard