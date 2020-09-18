
import time
from typing import Optional
from loguru import logger

from mcstatus import MinecraftServer
from mcstatus.querier import QueryResponse

from app.config import SERVER_IP


REQUESTS_TIMEOUT = 60


class ServerInfo:
    info = None
    request_time = None

    @classmethod
    def get_info(cls) -> Optional[QueryResponse]:
        if cls.request_time is not None and cls.request_time > time.time() - REQUESTS_TIMEOUT:
            logger.info("Returned preserved info")
            return cls.info

        cls.request_time = time.time()
        try:
            cls.info = MinecraftServer(SERVER_IP).query()
            logger.info("The server responded")
        except Exception as e:
            cls.info = None
            logger.error(e)

        return cls.info
