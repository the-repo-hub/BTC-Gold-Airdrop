## BTC-GOLD-AIRDROP

Асинхронный телеграм-бот для регистрации и верификации участников раздачи криптовалюты.


### Функционал

1. Сохраняет полную информацию об участниках раздачи
2. Верифицирует кошельки и подписки на социальные сети
3. Оповещает администраторов о новых участниках раздачи
4. Реализована система обратной связи в виде жалоб, интеграция жалоб с почтой


### Установка
```bash
git clone https://github.com/the-repo-hub/BTC-Gold-Airdrop
cd BTC-Gold-Airdrop
poetry install
```
В корне должен быть .env файл со следующими ключами:
```dotenv
BOT_NAME # bot name
COIN_NAME # coin name
SUPPORTER_ID # support telegram ID(integer)
OWNER # telegram ID of the future owner(integer)
BOT_TOKEN # telegram bot token
ADMIN_EMAIL # telegram bot admin email (for feedback)
NOTIFICATION_EMAIL # email for automated notifications to admin about registration or issues.
NOTIFICATION_EMAIL_PASSWORD # bot email password
TELEGRAM_GROUP_ID # group to discuss the new currency
TELEGRAM_GROUP_URL # url of this group
INSTAGRAM_URL # Instagram group url
TWITTER_GROUP_ID # twitter group
TWITTER_TOKEN # twitter token
TWITTER_URL # url of twitter group
POSTGRES_HOST
POSTGRES_USER
POSTGRES_PASSWORD
POSTGRES_DB
DATABASE_URL
```

В файле messages_config.yaml можно изменить содержание основных сообщений

### Запуск
```bash
docker-compose up -d
```
