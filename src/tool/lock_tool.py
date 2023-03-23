import asyncio
from functools import wraps
from typing import Callable


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
