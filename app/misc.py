from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.redis import RedisStorage2
from loguru import logger

from app import config

bot = Bot(config.TELEGRAM_TOKEN, parse_mode=types.ParseMode.HTML)
storage = RedisStorage2(host=config.REDIS_HOST, port=config.REDIS_PORT, db=config.REDIS_DB_FSM)
dp = Dispatcher(bot, storage=storage)


def setup():
    from app import filters
    from app import middlewares
    from app.utils import executor

    middlewares.setup(dp)
    filters.setup(dp)
    executor.setup()

    logger.info("Configure handlers...")
    # noinspection PyUnresolvedReferences
    import app.handlers
