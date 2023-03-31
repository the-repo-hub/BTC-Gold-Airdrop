import aiogram.utils.exceptions
from aiogram import executor, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from bot import AirdropBot
import aiohttp
from models import *
import aiosmtplib
from asyncio import sleep
from email.message import EmailMessage


bot = AirdropBot()
dp = Dispatcher(bot, storage=MemoryStorage())
base = Base('base.db')


def get_start_keyboard():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('✅ Join Airdrop')
    keyboard.add('👤 My Profile')
    keyboard.add('❌ Cancel')
    keyboard.add('👥 Support')
    return keyboard


def get_submit_keyboard():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('✍️ Submit Details')
    keyboard.add('🆔 I want to specify a referral token')
    keyboard.add('⬅️ Back')
    keyboard.add('👥 Support')
    return keyboard


def get_cancel_keyboard():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('❌ Cancel')
    return keyboard


def get_profile_keyboard():
    keyboard = types.ReplyKeyboardMarkup(one_time_keyboard=True, resize_keyboard=True)
    keyboard.add('✅ Join Airdrop')
    keyboard.add('⬅️ Back')
    return keyboard


async def check_instagram(m: types.Message, instagram_username: str):
    return True


async def check_twitter(m: types.Message, session: aiohttp.ClientSession, twitter_username: str):
    if base.get_user_by_id(m.from_user.id).twitter_username == twitter_username:
        return True
    html = await session.get(f'https://api.twitter.com/2/users/{bot.twitter_group_id}/followers')
    if html.status == 200:
        json: dict = await html.json()
        users = json.get('data')
        for user in users:
            if user['username'] == twitter_username:
                return True
        await m.answer('❌ Your username was not found in followers')
        return False
    else:
        print(html.status)
        return True


def check_email(email: str):
    if '@' in email and '.' in email:
        return True
    return False


def check_wallet(wallet: str):
    if wallet[1] == 'x':
        return True
    return False


async def send_email_message(msg: str, subject: str):
    message = EmailMessage()
    message['Subject'] = subject
    message.set_content(msg)
    await aiosmtplib.send(message,
                          username=bot.bots_email,
                          password=bot.bots_password,
                          sender=bot.bots_email,
                          recipients=[bot.email],
                          hostname="smtp.gmail.com",
                          port=465,
                          use_tls=True)
    return True


@dp.message_handler(state=Checking.wallet_waiting)
async def done_page(m: types.Message, state: FSMContext):
    if m.text == '❌ Cancel':
        await submit_details_page(m)
        await state.finish()
    elif m.text == '/terms':
        await terms(m, reply_markup=get_cancel_keyboard())
    else:
        result = check_wallet(m.text)
        if result:
            base.set_user_field(m.from_user.id, 'wallet_address', m.text)
            base.set_user_field(m.from_user.id, 'validated', 1)
            user = base.get_user_by_id(m.from_user.id)
            text = bot.get_congratulations_text(user)
            await m.answer(text, reply_markup=get_start_keyboard())
            await state.finish()
            text = 'We have a new user!\n\n' + user.get_profile_text()
            await send_email_message(text, 'New participant!')
            await bot.send_message(bot.owner, text)
            # await bot.send_message(bot.supporter_id, text)
        else:
            await m.answer('❌ Wallet is not valid, try again')


@dp.message_handler(state=Checking.email_waiting)
async def wallet_type_page(m: types.Message, state: FSMContext):
    if m.text == '❌ Cancel':
        await submit_details_page(m)
        await state.finish()
    else:
        result = check_email(m.text)
        if result:
            base.set_user_field(m.from_user.id, 'email', m.text)
            await m.answer('✔️ Your email was accepted!\n\n'
                           f'Type your {bot.coin_name} address:\n\n'
                           f'Instructions for receiving a wallet: /terms', reply_markup=get_cancel_keyboard())
            await Checking.wallet_waiting.set()
        else:
            await m.answer('❌ Email is not valid, try again')


@dp.message_handler(state=Checking.instagram_waiting)
async def email_type_page(m: types.Message, state: FSMContext):
    if m.text == '❌ Cancel':
        await submit_details_page(m)
        await state.finish()
    else:
        instagram_username = m.text
        if '@' == m.text[0]:
            instagram_username = m.text[1:]
        result = await check_instagram(m, instagram_username)
        if result:
            base.set_user_field(m.from_user.id, 'instagram_username', instagram_username)
            await m.answer('✔️ Your instagram was accepted!\n\n'
                           f'Type your email address:\n\n'
                           f'Our email address: {bot.email}',
                           reply_markup=get_cancel_keyboard())
            await Checking.email_waiting.set()
        else:
            await m.answer('❌ Instagram is not valid, try again')


@dp.message_handler(state=Checking.twitter_waiting)
async def instagram_type_page(m: types.Message, state: FSMContext):
    if m.text == '❌ Cancel':
        await submit_details_page(m)
        await state.finish()
    else:
        twitter_username = m.text
        if '@' == m.text[0]:
            twitter_username = m.text[1:]
        async with aiohttp.ClientSession(headers=bot.twitter_headers) as session:
            result = await check_twitter(m, session, twitter_username)
            if result:
                base.set_user_field(user_id=m.from_user.id, field='twitter_username', content=twitter_username)
                await m.answer('✔️ Your twitter was accepted!\n\n'
                               'Type your instagram username to check presence in community:\n\n'
                               f'Our instagram page: {bot.instagram_url}',
                               reply_markup=get_cancel_keyboard())
                await Checking.instagram_waiting.set()


@dp.message_handler(lambda m: m.text == '✍️ Submit Details', lambda m: m.from_user.id == m.chat.id)
@base.user_decorator
async def twitter_type_page(m: types.Message):
    try:
        await bot.get_chat_member(bot.telegram_group_id, m.from_user.id)
        await bot.send_message(m.chat.id, f'Type your twitter username to check presence in community:\n\n'
                                          f'Our twitter page: {bot.twitter_url}',
                               reply_markup=get_cancel_keyboard())
        await Checking.twitter_waiting.set()
    except aiogram.utils.exceptions.BadRequest:
        await m.answer('❌ You need to join a group to get started', reply_markup=get_submit_keyboard())


@dp.message_handler(lambda m: m.text == '✅ Join Airdrop', lambda m: m.from_user.id == m.chat.id)
@base.user_decorator
async def submit_details_page(m: types.Message):
    text = '📢 Airdrop Rules\n\n' \
           '✏️ Mandatory Tasks:\n' \
           f'🔹️ Join our Telegram Channel {bot.telegram_url}\n' \
           f'🔹️ Follow our Twitter {bot.twitter_url}\n' \
           f'🔹️ Follow our Instagram {bot.instagram_url}\n\n' \
           f'🔹️ Our e-mail for feedback: {bot.email}\n\n' \
           'Complete all tasks then click “Submit Details” to verify you have completed the tasks.'
    await m.answer(text, reply_markup=get_submit_keyboard())


@dp.message_handler(lambda m: m.text == '❌ Cancel', lambda m: m.from_user.id == m.chat.id)
@base.user_decorator
async def cancel_page(m: types.Message):
    text = "I'm sorry you couldn't stand the terms, remember, you can always change your mind"
    await m.answer(text, reply_markup=get_start_keyboard())


@dp.message_handler(lambda m: m.text == '👤 My Profile', lambda m: m.from_user.id == m.chat.id)
@base.user_decorator
async def profile_page(m: types.Message):
    user = base.get_user_by_id(m.from_user.id)
    text = "👤 Your Profile:\n\n" + user.get_profile_text() + f"\n\nUse your referral wallet: {user.wallet} to give it your friends!"
    await m.answer(text, reply_markup=get_profile_keyboard())


@dp.message_handler(lambda m: m.from_user.id == m.chat.id and (m.text == '⬅️ Back' or m.text == '/start'))
@base.user_decorator
async def start_page(m: types.Message):
    await m.answer(bot.get_terms_and_conditions_text())
    await m.answer(bot.get_start_page_text(m), reply_markup=get_start_keyboard())


@dp.message_handler(state=Support.problem_waiting)
async def trouble_message_handler(m: types.Message, state: FSMContext):
    if m.text == '❌ Cancel':
        await state.finish()
        await start_page(m)
    else:
        await state.finish()
        await m.answer('Your complaint has been forwarded to support, your issue will be resolved soon',
                       reply_markup=get_start_keyboard())
        user = base.get_user_by_id(m.from_user.id)
        text = f"We have a trouble!\n\n" \
               f"'{m.text}'\n\n" \
               f"{user.get_profile_text()}"
        await bot.send_message(bot.owner, text)
        await send_email_message(msg=text, subject='Trouble message!')


@dp.message_handler(lambda m: m.text == '👥 Support' and m.from_user.id == m.chat.id)
@base.user_decorator
async def support(m: types.Message):
    text = 'We are very sorry to hear that you are having trouble, please describe your issue:'
    await m.answer(text, reply_markup=get_cancel_keyboard())
    await Support.problem_waiting.set()


@dp.message_handler(state=Referral.wallet_waiting)
async def email_type_page(m: types.Message, state: FSMContext):
    if m.text == '❌ Cancel':
        await submit_details_page(m)
        await state.finish()
    elif m.text not in base.get_all_fields_in_column('wallet_address'):
        await m.answer('❌ The wallet was not found in the list of participants, try again',
                       reply_markup=get_cancel_keyboard())
    elif m.text == base.get_user_by_id(m.from_user.id).wallet:
        await m.answer("❌ You can't enter your wallet", reply_markup=get_cancel_keyboard())
    else:
        base.set_user_field(m.from_user.id, 'referral_wallet', m.text)
        await m.answer(f"Great! You have entered your invite's wallet, he will receive 1 {bot.coin_name}!")
        await state.finish()
        await sleep(3)
        await submit_details_page(m)


@dp.message_handler(lambda m: m.text == '🆔 I want to specify a referral token' and m.from_user.id == m.chat.id)
@base.user_decorator
async def referral(m: types.Message):
    text = f"Specify the invitation token (invite's {bot.coin_name} wallet):"
    await m.answer(text, reply_markup=get_cancel_keyboard())
    await Referral.wallet_waiting.set()


@dp.message_handler(lambda m: m.from_user.id == m.chat.id, commands=['terms'])
async def terms(m: types.Message, reply_markup: types.ReplyKeyboardMarkup = None):
    await m.answer(bot.get_terms_and_conditions_text(), reply_markup=reply_markup)


@dp.message_handler(lambda m: m.from_user.id == m.chat.id)
@base.user_decorator
async def any_msg(m: types.Message):
    await m.answer(bot.get_any_text(), reply_markup=get_start_keyboard())


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=False)
