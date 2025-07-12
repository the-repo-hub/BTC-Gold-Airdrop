from typing import Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject
from cachetools import LRUCache
from sqlalchemy import Column, Integer, String, DateTime, func, select
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

from configs_processor import Config

Base = declarative_base()
engine = create_async_engine(Config.DATABASE_URL)
Session = async_sessionmaker(bind=engine)


class User(Base):
    __tablename__ = 'users'
    __table_args__ = {'postgresql_autocreate': True}
    pk = Column(Integer, primary_key=True, autoincrement=True)
    telegram_id = Column(Integer, unique=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    wallet = Column(String(255), nullable=True)
    referral_wallet = Column(String(255), nullable=True)
    twitter_username = Column(String(255), nullable=True)
    instagram_username = Column(String(255), nullable=True)
    email = Column(String(255), nullable=True)
    language_code = Column(String(10))
    registered_on = Column(DateTime, nullable=False, default=func.now())


async def ensure_user(message: TelegramObject, session: AsyncSession) -> User:
    result = await session.execute(select(User).filter_by(user_id=message.from_user.id))
    user = result.scalar_one_or_none()
    if user is None:
        session.add(
            User(
                telegram_id=message.from_user.id,
                username=message.from_user.username,
                first_name=message.from_user.first_name,
                last_name=message.from_user.last_name,
                language_code=message.from_user.wallet,
            )
        )
        await session.commit()
    return user


class UserMiddleware(BaseMiddleware):

    def __init__(self, size=1000):
        self.user_cache = LRUCache(maxsize=size)

    async def __call__(self, handler: Callable, event: TelegramObject, data):
        user = self.user_cache.get(event.from_user.id)
        if user is None:
            async with Session() as session:
                user = await ensure_user(event, session)
                self.user_cache[event.from_user.id] = user
        return await handler(event, data, user)
