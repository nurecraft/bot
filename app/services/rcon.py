import time
import re

from loguru import logger

from app.config import SERVER_IP, RCON_SECRET

from mcrcon import MCRcon


REQUESTS_TIMEOUT = 60


class RCONCommandSender:
    values = {}
    request_time = {}

    @staticmethod
    def send(cmd: str) -> str:
        with MCRcon(SERVER_IP, RCON_SECRET) as mcr:
            responce = mcr.command(cmd)
        return re.sub(r"§\w", "", responce)

    @classmethod
    def send_with_timeout(cls, cmd: str):
        if cls.request_time.get(cmd) is not None and cls.request_time.get(cmd) > time.time() - REQUESTS_TIMEOUT:
            logger.info("Returned preserved command responce")
            return cls.values.get(cmd)

        cls.values[cmd] = cls.send(cmd)
        cls.request_time[cmd] = time.time()

        logger.info("Get new command responce")
        return cls.values[cmd]