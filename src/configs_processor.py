import os

import yaml
from dotenv import load_dotenv

class Messages:
    def __init__(self, config):
        messages = config['messages']
        self.start = messages["start_message"]
        self.terms_and_conditions = messages["terms_and_conditions_message"]
        self.unknown= messages["unknown_message"]
        self.congratulations = messages["congratulations"]
        self.specify_token = messages["specify_token"]
        self.wallet_not_found = messages["wallet_not_found"]
        self.support = messages["support"]
        self.profile = messages["profile"]
        self.cant_enter_wallet = messages["cant_enter_wallet"]
        self.cant_submit_terms = messages["cant_submit_terms"]
        self.join = messages["join"]
        self.new_profile = messages["new_profile"]
        self.email_valid = messages["email_valid"]
        self.email_invalid = messages["email_invalid"]
        self.instagram_valid = messages["instagram_valid"]
        self.instagram_invalid = messages["instagram_invalid"]
        self.you_need_to_join = messages["you_need_to_join"]
        self.twitter_was_accepted = messages["twitter_was_accepted"]
        self.complaint_sent = messages["complaint_sent"]
        self.we_have_trouble = messages["we_have_trouble"]
        self.username_not_in_twitter_followers = messages["username_not_in_twitter_followers"]

class Buttons:
    def __init__(self, config):
        buttons = config['buttons']
        self.join = buttons["join"]
        self.cancel = buttons["cancel"]
        self.profile = buttons["profile"]
        self.support = buttons["support"]
        self.back = buttons["back"]
        self.specify_referral = buttons["specify_referral"]
        self.submit_details = buttons["submit_details"]

class Checks:
    def __init__(self, config):
        checks = config['checks']
        self.instagram = checks["instagram"]
        self.twitter = checks["twitter"]

class Config:
    load_dotenv()
    BOT_TOKEN = os.getenv('TOKEN')
    DATABASE_URL = os.getenv('DATABASE_URL')
    BOT_NAME = os.getenv('BOT_NAME')
    COIN_NAME = os.getenv('COIN_NAME')
    SUPPORTER_ID = os.getenv('SUPPORTER_ID')
    OWNER = os.getenv('OWNER')
    ADMIN_EMAIL = os.getenv('ADMIN_EMAIL')
    NOTIFICATION_EMAIL = os.getenv('NOTIFICATION_EMAIL')
    NOTIFICATION_EMAIL_PASSWORD = os.getenv('NOTIFICATION_EMAIL_PASSWORD')
    TELEGRAM_GROUP_ID = os.getenv('TELEGRAM_GROUP_ID')
    TELEGRAM_GROUP_URL = os.getenv('TELEGRAM_GROUP_URL')
    INSTAGRAM_URL = os.getenv('INSTAGRAM_URL')
    TWITTER_GROUP_ID = os.getenv('TWITTER_GROUP_ID')
    TWITTER_TOKEN = os.getenv('TWITTER_TOKEN')
    TWITTER_URL = os.getenv('TWITTER_URL')
    with open("../messages_config.yaml", 'r', encoding="utf-8") as f:
        config = yaml.safe_load(f)
    messages = Messages(config)
    buttons = Buttons(config)
    checks = Checks(config)
    twitter_headers = {
        "Authorization": f"Bearer {TWITTER_TOKEN}",
        "User-Agent": "v2LikedTweetsPython",
    }
