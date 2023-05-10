from datetime import time
import os
from aiologger.levels import LogLevel
from aiologger import Logger
from aiologger.handlers.files import AsyncTimedRotatingFileHandler, RolloverInterval

from ..src.tool.map_tool import MapKey
from .env import PROJECT_ROOT, ProjectEnv


LOG_ROOT = os.path.join(PROJECT_ROOT, 'log')
LOG_NAME = os.path.join(LOG_ROOT, 'local.log')


class LoggerLocal:
    @staticmethod
    @MapKey()
    async def get_logger(level: LogLevel = LogLevel.INFO):
        project_name = await ProjectEnv.get_name()
        logger = Logger(name=project_name, level=level)
        handler_file = AsyncTimedRotatingFileHandler(
            filename=LOG_NAME, backup_count=4,
            when=RolloverInterval.SATURDAYS, interval=1, at_time=time(hour=5),
        )
        logger.add_handler(handler_file)
        return logger
    pass
