import re
from asyncio import sleep, run
from email.message import EmailMessage
from http import HTTPStatus
from logging import getLogger

import aiohttp
import aiosmtplib
from aiogram import Bot, Dispatcher, types, F
from aiogram import exceptions
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.memory import MemoryStorage
from sqlalchemy import select

from configs_processor import Config
from keyboard import Keyboards
from models import UserMiddleware, User, Session
from states import Referral, Checking, Support

bot = Bot(token=Config.BOT_TOKEN)
dp = Dispatcher(storage=MemoryStorage())
middleware = UserMiddleware()
dp.update.outer_middleware(middleware)
keyboards = Keyboards()
logger = getLogger(Config.BOT_NAME)

async def instagram_subscription_checker(m: types.Message, instagram_username: str):
    #todo
    return True

async def twitter_subscription_checker(message: types.Message, session: aiohttp.ClientSession, twitter_username: str, user: User):
    if user.twitter_username == twitter_username:
        return True
    html = await session.get(f'https://api.twitter.com/2/users/{Config.TWITTER_GROUP_ID}/followers')
    if html.status == HTTPStatus.OK:
        json: dict = await html.json()
        users = set(json.get('data'))
        if twitter_username in users:
            return True
        await message.answer(Config.messages.username_not_in_twitter_followers)
        return False
    else:
        print(html.status)
        return True


def email_is_valid(email: str):
    return re.match(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$", email)

def wallet_is_valid(wallet: str):
    return re.match(r'^0x[a-fA-F0-9]{40}$', wallet)

async def send_email_message(msg: str, subject: str):
    message = EmailMessage()
    message['Subject'] = subject
    message.set_content(msg)
    await aiosmtplib.send(
        message,
        username=Config.NOTIFICATION_EMAIL,
        password=Config.NOTIFICATION_EMAIL_PASSWORD,
        sender=Config.NOTIFICATION_EMAIL,
        recipients=(Config.ADMIN_EMAIL,),
        hostname="smtp.gmail.com",
        port=465,
        use_tls=True
    )

@dp.message(Command('terms'))
async def terms_callback(message: types.Message):
    await message.answer(text=Config.messages.terms_and_conditions)

@dp.message(F.text == Config.buttons.join)
async def join_page(message: types.Message):
    text = Config.messages.join
    await message.answer(text, reply_markup=keyboards.submit_keyboard)

@dp.message(state=Checking.wallet_waiting)
async def done_page(message: types.Message, state: FSMContext, user: User):
    if message.text == Config.buttons.cancel:
        await join_page(message)
        await state.clear()
    elif message.text == '/terms':
        await terms_callback(message, reply_markup=keyboards.cancel_keyboard)
    else:
        result = wallet_is_valid(message.text)
        if result:
            user.wallet = message.text.strip().rstrip()
            text = Config.messages.congratulations
            await message.answer(text, reply_markup=keyboards.start_keyboard)
            await state.clear()
            text = 'We have a new user!\n\n' + Config.messages.profile
            await send_email_message(text, 'New participant!')
            await bot.send_message(Config.OWNER, text)
            # await bot.send_message(bot.supporter_id, text)
        else:
            await message.answer('❌ Wallet is not valid, try again')


@dp.message(state=Checking.email_waiting)
async def wallet_type_page(message: types.Message, state: FSMContext, user: User):
    if message.text == Config.buttons.cancel:
        await join_page(message)
        await state.clear()
    else:
        result = email_is_valid(message.text)
        if result:
            user.email = message.text
            await message.answer(Config.messages.email_valid, reply_markup=keyboards.cancel_keyboard)
            await Checking.wallet_waiting.set()
        else:
            await message.answer(Config.messages.email_invalid)


@dp.message(state=Checking.instagram_waiting)
async def email_type_page(message: types.Message, state: FSMContext, user: User):
    if message.text == Config.buttons.cancel:
        await join_page(message)
        await state.clear()
    else:
        instagram_username = message.text
        if '@' == message.text[0]:
            instagram_username = message.text[1:]
        result = await instagram_subscription_checker(message, instagram_username)
        if result:
            user.instagram_username = instagram_username
            await message.answer(Config.messages.instagram_valid, reply_markup=keyboards.cancel_keyboard)
            await Checking.email_waiting.set()
        else:
            await message.answer(Config.messages.instagram_invalid)


@dp.message(state=Checking.twitter_waiting)
async def instagram_type_page(message: types.Message, state: FSMContext, user: User):
    if message.text == Config.buttons.cancel:
        await join_page(message)
        await state.clear()
        return
    twitter_username = message.text.strip().rstrip()
    if '@' == message.text[0]:
        twitter_username = message.text[1:]
    async with aiohttp.ClientSession(headers=Config.twitter_headers) as session:
        result = await twitter_subscription_checker(message, session, twitter_username, user)
        if result:
            user.twitter_username = twitter_username
            await message.answer(Config.messages.twitter_was_accepted, reply_markup=keyboards.cancel_keyboard)
            await Checking.instagram_waiting.set()


@dp.message(F.text == Config.buttons.submit_details)
async def twitter_type_page(message: types.Message):
    try:
        await bot.get_chat_member(Config.TELEGRAM_GROUP_ID, message.from_user.id)
    except exceptions.TelegramBadRequest:
        await message.answer(Config.messages.you_need_to_join, reply_markup=keyboards.submit_keyboard)
    else:
        await bot.send_message(message.chat.id, f'Type your twitter username to check presence in community:\n\n'
                                          f'Our twitter page: {Config.TWITTER_URL}',
                               reply_markup=keyboards.cancel_keyboard)
        await Checking.twitter_waiting.set()

@dp.message(F.text == Config.buttons.cancel)
async def cancel_page(message: types.Message):
    await message.answer(text=Config.messages.cant_submit_terms, reply_markup=keyboards.start_keyboard)


@dp.message(F.text == Config.buttons.profile)
async def profile_page(message: types.Message):
    await message.answer(text=Config.messages.profile, reply_markup=keyboards.profile_keyboard)


@dp.message(F.text == Config.buttons.back or CommandStart())
async def start_page(message: types.Message):
    await message.answer(text=Config.messages.terms_and_conditions)
    await message.answer(Config.messages.start, reply_markup=keyboards.start_keyboard)


@dp.message(state=Support.problem_waiting)
async def trouble_message_handler(message: types.Message, state: FSMContext, user: User):
    if message.text == Config.buttons.cancel:
        await state.clear()
        await start_page(message)
    else:
        await state.clear()
        await message.answer(
            text=Config.messages.complaint_sent,
            reply_markup=keyboards.start_keyboard,
        )
        text = Config.messages.we_have_trouble
        await bot.send_message(Config.OWNER, text)
        await send_email_message(msg=text, subject='Trouble message!')


@dp.message(F.text == Config.buttons.support)
async def support(message: types.Message):
    await message.answer(Config.messages.support, reply_markup=keyboards.cancel_keyboard)
    await Support.problem_waiting.set()


@dp.message(state=Referral.wallet_waiting)
async def email_type_page(message: types.Message, state: FSMContext):
    if message.text == Config.buttons.cancel:
        await join_page(message)
        await state.clear()
        return
    async with Session() as session:
        stmt = select(User).where(wallet=message.text)
        user = (await session.execute(stmt)).scalar_or_none()
        if not user:
            await message.answer(
                text=Config.messages.wallet_not_found,
                reply_markup=keyboards.cancel_keyboard
            )
        elif message.from_user.id == user.telegram_id:
            await message.answer("❌ You can't enter your wallet", reply_markup=keyboards.cancel_keyboard)
        else:
            user.referral_wallet = message.text
            session.commit()
            await message.answer(f"Great! You have entered your invite's wallet, he will receive 1 {Config.COIN_NAME}!")
            await state.clear()
            await sleep(3)
            await join_page(message)


@dp.message(lambda message: message.text == Config.messages.specify_token)
async def referral(message: types.Message):
    await message.answer(Config.messages, reply_markup=keyboards.cancel_keyboard)
    await Referral.wallet_waiting.set()

@dp.message(CommandStart())
async def any_msg(message: types.Message):
    await message.answer(text=Config.messages.start, reply_markup=keyboards.start_keyboard)


if __name__ == '__main__':
    run(dp.start_polling())
