from typing import Callable, Dict
from aiologger.levels import LogLevel
from .func import MockFunc


class MockLog:
    @staticmethod
    async def level_dict(level: LogLevel) -> Dict[LogLevel, Callable]:
        return {
            LogLevel.DEBUG: MockFunc.norm_async,
            LogLevel.INFO: MockFunc.norm_async,
            LogLevel.WARNING: MockFunc.norm_async,
            LogLevel.ERROR: MockFunc.norm_async,
            LogLevel.CRITICAL: MockFunc.norm_async,
        }
    pass
