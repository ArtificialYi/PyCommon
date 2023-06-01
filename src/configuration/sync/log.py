import asyncio
from datetime import time
from logging.handlers import TimedRotatingFileHandler
import os
import logging
from logging import Logger

from ...tool.map_tool import MapKey
from .env import PROJECT_ROOT, ProjectEnv


LOG_ROOT = os.path.join(PROJECT_ROOT, 'log')
LOG_NAME = os.path.join(LOG_ROOT, 'local.log')


class LoggerLocal:
    LEVEL = logging.INFO

    @staticmethod
    @MapKey()
    def get_logger() -> Logger:
        project_name = ProjectEnv.get_name()
        logger = logging.getLogger(name=project_name)
        logger.setLevel(LoggerLocal.LEVEL)

        handler_file = TimedRotatingFileHandler(
            filename=LOG_NAME, backupCount=4,
            when='S', interval=1, atTime=time(hour=5),
        )
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        handler_file.setFormatter(formatter)

        logger.addHandler(handler_file)
        return logger

    @staticmethod
    def debug(*args, **kwds):
        logger: Logger = LoggerLocal.get_logger()
        logger.debug(*args, **kwds)
        pass

    @staticmethod
    def info(*args, **kwds):
        logger: Logger = LoggerLocal.get_logger()
        logger.info(*args, **kwds)
        pass

    @staticmethod
    def warning(*args, **kwds):
        logger: Logger = LoggerLocal.get_logger()
        logger.warning(*args, **kwds)
        pass

    @staticmethod
    def error(*args, **kwds):
        logger: Logger = LoggerLocal.get_logger()
        logger.error(*args, **kwds)
        pass

    @staticmethod
    def exception(e: BaseException, *args, **kwds):
        logger: Logger = LoggerLocal.get_logger()
        if isinstance(e, Exception):
            logger.error(*args, **kwds)
            return

        if isinstance(e, asyncio.CancelledError):
            logger.warning(*args, **kwds)
            return

        logger.exception(e, *args, **kwds)
        pass
    pass
