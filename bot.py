from aiogram import Bot
from models import User


class AirdropBot(Bot):
    """This is a project for one of my clients - telegram bot for airdrop. For normal operation, the code must be
    supplemented with variables in this file. Variables have been cleared, because they had a private information"""
    bot_name = 'BTC GOLD Airdrop Bot'  # bot name
    coin_name = 'BTC GOLD'  # coin name
    supporter_id = 123456789  # support telegram ID(integer)
    owner = 123456789  # telegram ID of the future owner(integer)
    token = 'Token Sample'  # telegram bot token

    email = 'example@example.com'  # telegram bot admin email (for feedback)
    bots_email = 'example@example.com'  # email for automated notifications to admin about registration or issues.
    bots_password = 'password'  # bot email password

    telegram_group_id = -123456789  # group to discuss the new currency
    telegram_url = 'https://t.me/Btc_Gold_365'  # url of this group

    instagram_url = 'https://www.instagram.com/btcgold703'  # Instagram group url

    twitter_group_id = 123456789  # twitter group
    twitter_token = 'some token' # twitter token
    twitter_url = 'https://twitter.com/BitCoinGold19' # url of twitter group
    twitter_headers = {"Authorization": f"Bearer {twitter_token}",
                       "User-Agent": "v2LikedTweetsPython"} # headers

    def __init__(self):
        super(AirdropBot, self).__init__(self.token)

    @classmethod
    def get_congratulations_text(cls, user: User):
        text = "Congratulations!\n\n" \
               "You have joined to airdrop, follow the news in our communities:\n\n" \
               f"Our twitter: {cls.twitter_url}\n" \
               f"Our instagram: {cls.instagram_url}\n" \
               f"Our telegram group: {cls.telegram_url}"
        text += f"\n\nUse your referal wallet: {user.wallet} to give it your friends!"
        return text

    def get_start_page_text(self, m):
        text = f"🗣 Hello, {m.from_user.first_name}! I am your friendly {self.bot_name}\n\n" \
               "✅ Please do the required tasks to be eligible to get airdrop tokens.\n" \
               f"🔸 For Joining - Get - 5 {self.coin_name} = 5 grams pure 24 Carat Gold\n" \
               f"⭐️ For each referral - Get - 1 {self.coin_name} = 1 grams of pure 24 carat Gold\n" \
               f"📘 By Participating you are agreeing to the {self.bot_name} (Airdrop) Program Terms and Conditions (See previous message). Please see pinned post for more information.\n\n" \
               "Click 'Join Airdrop' to proceed"
        return text

    @staticmethod
    def get_terms_and_conditions_text():
        text = "How to add get (BTCGO) token to your Metamask wallet?\n" \
               "VIEW THIS YOUTUBE VIDEO INORDER TO CREATE A SMARTCHAIN.\n\n" \
               "https://www.youtube.com/watch?v=kzQm5iM-Hkw\n\n" \
               "Open metamask and select Binance smart chain network. Click on import token and copy the contract address below:\n\n" \
               "0x462BfA1f1102a367d3e8B7E9a6698427808b2C5e\n\n" \
               "Then paste contract address in contract field in your Metamask Wallet. Once you add contract address, Decimals & name of the contract will appear. Click on add token to see GET tokens in your wallet.\n\n" \
               "Terms & Condition of the (BTCGO) Airdrop:\n\n" \
               "1) Please follow the instruction given on the BOT page.\n" \
               "2) Every account is entitle to 5 BTCGO tokens = 5 grams of gold (Only valid when the project is listed with one or more major Crypto Exchanges between November 2022 and March 2023).\n" \
               "3) Every referral will give the referrer 1 BTCGO token.\n" \
               "4) We are going to launch the BTC GOLD ico between November 2022 and March 2023.We keep all our token holders informed on tweeter or telegram."
        return text

    @staticmethod
    def get_any_text():
        text = "❌ Unknown Command!\n\n" \
               "You have send a Message directly into the Bot's chat or\n" \
               "Menu structure has been modified by Admin.\n\n" \
               "ℹ️ Do not send Messages directly to the Bot or reload the Menu by pressing /start"
        return text
