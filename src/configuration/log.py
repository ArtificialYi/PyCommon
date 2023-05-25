import asyncio
from datetime import time
import os
from aiologger.levels import LogLevel
from aiologger import Logger
from aiologger.handlers.files import AsyncTimedRotatingFileHandler, RolloverInterval
from aiologger.formatters.base import Formatter

from ..tool.map_tool import MapKey
from .env import PROJECT_ROOT, ProjectEnv


LOG_ROOT = os.path.join(PROJECT_ROOT, 'log')
LOG_NAME = os.path.join(LOG_ROOT, 'local.log')


class LoggerLocal:
    LEVEL = LogLevel.INFO

    @staticmethod
    @MapKey()
    async def get_logger() -> Logger:
        project_name = await ProjectEnv.get_name()
        logger = Logger(name=project_name, level=LoggerLocal.LEVEL)
        handler_file = AsyncTimedRotatingFileHandler(
            filename=LOG_NAME, backup_count=4,
            when=RolloverInterval.SATURDAYS, interval=1, at_time=time(hour=5),
        )
        handler_file.formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger.add_handler(handler_file)
        return logger

    @staticmethod
    async def debug(*args, **kwds):
        logger: Logger = await LoggerLocal.get_logger()
        await logger.debug(*args, **kwds)

    @staticmethod
    async def info(*args, **kwds):
        logger: Logger = await LoggerLocal.get_logger()
        await logger.info(*args, **kwds)

    @staticmethod
    async def warning(*args, **kwds):
        logger: Logger = await LoggerLocal.get_logger()
        await logger.warning(*args, **kwds)

    @staticmethod
    async def error(*args, **kwds):
        logger: Logger = await LoggerLocal.get_logger()
        await logger.error(*args, **kwds)

    @staticmethod
    async def exception(e: BaseException, *args, **kwds):
        logger: Logger = await LoggerLocal.get_logger()
        if isinstance(e, Exception):
            await logger.error(*args, **kwds)
            return

        if isinstance(e, asyncio.CancelledError):
            await logger.warning(*args, **kwds)
            return

        await logger.exception(e, *args, **kwds)

    @staticmethod
    async def shutdown():
        logger: Logger = await LoggerLocal.get_logger()
        await logger.shutdown()
    pass
