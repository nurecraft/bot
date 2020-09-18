import datetime
import time
import asyncio
from contextlib import suppress
from typing import List

from aiogram import Dispatcher
from aiogram.utils.exceptions import MessageToDeleteNotFound
from aiogram.utils.executor import Executor
from loguru import logger

from app import config
from app.misc import bot
from app.services.apscheduller import scheduler
from app.utils.redis import BaseRedis

JOB_PREFIX = "join_cleaner"


class JoinListService(BaseRedis):
    def __init__(self, prefix="chat", *args, **kwargs):
        super(JoinListService, self).__init__(*args, **kwargs)
        self.prefix = prefix

    async def create_task(self, chat_id: int, message_id: int, user_id: int = 0,
                          prefix="default", delta=config.JOIN_MESSAGE_CLEANER):
        job_key = f"{JOB_PREFIX}:{prefix}:{chat_id}:{user_id}"

        kwargs = {
            "chat_id": chat_id,
            "message_id": message_id,
            "user_id": user_id,
            "kick": True if prefix == "join" else False
        }

        scheduler.add_job(
            join_expired,
            "date",
            id=job_key,
            run_date=datetime.datetime.utcnow() + delta,
            kwargs=kwargs,
        )

async def join_expired(chat_id: int, message_id: int, user_id: int, kick: bool):
    with suppress(MessageToDeleteNotFound):
        await bot.delete_message(chat_id, message_id)

    if kick:
        await bot.kick_chat_member(chat_id, user_id)
        await bot.unban_chat_member(chat_id, user_id)


join = JoinListService(
    host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB_JOIN_LIST
)


async def on_startup(dispatcher: Dispatcher):
    await join.connect()


async def on_shutdown(dispatcher: Dispatcher):
    await join.disconnect()


def setup(runner: Executor):
    runner.on_startup(on_startup)
    runner.on_shutdown(on_shutdown)
