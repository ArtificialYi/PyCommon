from datetime import time
import os
from aiologger.levels import LogLevel
from aiologger import Logger
from aiologger.handlers.files import AsyncTimedRotatingFileHandler, RolloverInterval
from aiologger.formatters.base import Formatter

from ..src.tool.base import BaseTool
from ..src.tool.map_tool import MapKey
from .env import PROJECT_ROOT, ProjectEnv


LOG_ROOT = os.path.join(PROJECT_ROOT, 'log')
LOG_NAME = os.path.join(LOG_ROOT, 'local.log')


class LoggerLocal:
    @staticmethod
    @MapKey(BaseTool.return_self)
    async def __get_logger(level: LogLevel = LogLevel.INFO) -> Logger:
        project_name = await ProjectEnv.get_name()
        logger = Logger(name=project_name, level=level)
        handler_file = AsyncTimedRotatingFileHandler(
            filename=LOG_NAME, backup_count=4,
            when=RolloverInterval.SATURDAYS, interval=1, at_time=time(hour=5),
        )
        handler_file.formatter = Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        logger.add_handler(handler_file)
        return logger

    @staticmethod
    async def debug(*args, **kwds):
        logger: Logger = await LoggerLocal.__get_logger()
        await logger.debug(*args, **kwds)

    @staticmethod
    async def info(*args, **kwds):
        logger: Logger = await LoggerLocal.__get_logger()
        await logger.info(*args, **kwds)

    @staticmethod
    async def warning(*args, **kwds):
        logger: Logger = await LoggerLocal.__get_logger()
        await logger.warning(*args, **kwds)

    @staticmethod
    async def error(*args, **kwds):
        logger: Logger = await LoggerLocal.__get_logger()
        await logger.error(*args, **kwds)
    pass
