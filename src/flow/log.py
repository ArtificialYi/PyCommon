import asyncio
from typing import Callable, Optional
from ..tool.map_tool import LockManage, MapKey
from ..tool.base import AsyncBase
from ..tool.func_tool import FuncTool, QueueException
from ...configuration.log import LoggerLocal
from ..tool.loop_tool import OrderApi
from aiologger.levels import LogLevel


class FlowLogger(OrderApi):
    def __init__(self, level: LogLevel, callback: Optional[Callable] = None) -> None:
        self.__level = level
        OrderApi.__init__(self, self.log, callback)

    async def log(self, level: LogLevel, msg: str):
        logger_dict = await LoggerLocal.level_dict(self.__level)
        await logger_dict[level](msg)
        pass
    pass


class LoggerApi:
    def __init__(self, level: LogLevel) -> None:
        self.__level = level
        self.__task = AsyncBase.get_done_task()
        self.__lock = LockManage()
        pass

    async def __flow_run(self, future: asyncio.Future):
        err_queue = QueueException()
        async with FlowLogger(self.__level, err_queue) as logger:
            future.set_result(logger)
            await err_queue.exception_loop(1)
            pass
        pass

    async def __get_logger(self) -> FlowLogger:
        async with self.__lock.get_lock():
            if self.__task.done():
                future: asyncio.Future[FlowLogger] = AsyncBase.get_future()
                self.__task = asyncio.create_task(self.__flow_run(future))
                self.__flow_logger = await future
                done, _ = await asyncio.wait([
                    self.__task, future
                ], return_when=asyncio.FIRST_COMPLETED)
                self.__flow_logger = done.pop().result()
            pass
        return self.__flow_logger  # type: ignore

    async def api(self, level: LogLevel, msg: str):
        flow_logger = await self.__get_logger()
        await flow_logger.log(level, msg)
        pass

    async def close(self):
        task = self.__task
        task.cancel()
        await FuncTool.await_no_cancel(task)
        pass
    pass


def get_level():
    return Logger.LEVEL


class Logger:
    LEVEL = LogLevel.INFO

    @classmethod
    def set_level(cls, level: LogLevel):
        cls.LEVEL = level
        pass

    @staticmethod
    @MapKey(get_level)
    def __get_api():
        return LoggerApi(get_level())

    @classmethod
    async def debug(cls, msg: str):
        api: LoggerApi = cls.__get_api()
        await api.api(LogLevel.DEBUG, msg)
        pass

    @classmethod
    async def info(cls, msg: str):
        api: LoggerApi = cls.__get_api()
        await api.api(LogLevel.INFO, msg)
        pass

    @classmethod
    async def warn(cls, msg: str):
        api: LoggerApi = cls.__get_api()
        await api.api(LogLevel.WARN, msg)
        pass

    @classmethod
    async def error(cls, msg: str):
        api: LoggerApi = cls.__get_api()
        await api.api(LogLevel.ERROR, msg)
        pass

    @classmethod
    async def critical(cls, msg: str):
        api: LoggerApi = cls.__get_api()
        await api.api(LogLevel.CRITICAL, msg)
        pass

    @classmethod
    async def close(cls):
        api: LoggerApi = cls.__get_api()
        await api.close()
        pass
    pass
