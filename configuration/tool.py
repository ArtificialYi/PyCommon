import asyncio
from configparser import ConfigParser
from functools import wraps
import os
from typing import Callable

import aiofiles


class ConfigTool:
    @staticmethod
    async def get_config(path: str):
        config = ConfigParser()
        if os.path.exists(path):
            async with aiofiles.open(path, 'r') as config_file:
                str_config = await config_file.read()
                config.read_string(str_config)
            pass
        return config

    @staticmethod
    def get_value(
        section: str, option: str, *config_lst: ConfigParser, default=''
    ):
        res = default
        for config in config_lst:
            res = config.get(section, option, fallback=res)
            pass
        return res
    pass


class DCLGlobalAsync:
    """全局唯一双检锁
    """
    def __init__(self) -> None:
        self.__field = None
        self.__lock = None
        pass

    def __call__(self, func: Callable) -> Callable:
        @wraps(func)
        async def func_async(*args, **kwds):
            return await self.__double_check_lock_action(func, *args, **kwds)
        return func_async

    async def __double_check_lock_action(self, func: Callable, *args, **kwds):
        if self.__field is not None:
            return self.__field

        async with self.__get_lock():
            if self.__field is not None:
                return self.__field

            self.__field = await func(*args, **kwds)
            pass
        return self.__field

    def __get_lock(self):
        if self.__lock is not None:
            return self.__lock

        self.__lock = asyncio.Lock()
        return self.__lock
    pass
