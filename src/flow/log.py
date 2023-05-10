from typing import Callable, Optional
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
