import asyncio
from functools import wraps
from typing import Callable, Union
from .base import AsyncBase


class MapKey:
    class Sync:
        def __init__(self, func_key: Union[Callable, None] = None) -> None:
            self.__map = dict()
            self.__func_key = func_key
            self.__iscoro_key = asyncio.iscoroutinefunction(func_key)
            pass

        def __call__(self, func_value: Callable) -> Callable:
            @wraps(func_value)
            def wrapper(*args, **kwds):
                key = self.__get_key(*args, **kwds)
                if self.__map.get(key, None) is None:
                    self.__map[key] = func_value(*args, **kwds)
                return self.__map[key]
            return wrapper

        def __get_key(self, *args, **kwds):
            if self.__func_key is None:
                return ''
            key_res = self.__func_key(*args, **kwds)
            if not self.__iscoro_key:
                return key_res
            task = AsyncBase.coro2task_exec(key_res)
            return task.result()
        pass

    class AsyncLock:
        def __init__(self, func_key: Union[Callable, None]) -> None:
            self.__map = dict()
            self.__func_key = func_key
            self.__iscoro = asyncio.iscoroutinefunction(func_key)
            self.__map_lock = dict()
            pass

        def __call__(self, func_value: Callable) -> Callable:
            @wraps(func_value)
            async def wrapper(*args, **kwds):
                return await self.__wrapper(func_value, *args, **kwds)
            return wrapper

        async def __wrapper(self, func_value: Callable, *args, **kwds):
            key = await self.__get_key(*args, **kwds)
            if self.__map.get(key, None) is not None:
                return self.__map[key]

            async with self.__get_lock():
                if self.__map.get(key, None) is not None:
                    return self.__map[key]
                self.__map[key] = await func_value(*args, **kwds)
            return self.__map[key]

        async def __get_key(self, *args, **kwds):
            if self.__func_key is None:
                return ''
            key_res = self.__func_key(*args, **kwds)
            return await key_res if self.__iscoro else key_res

        def __get_lock(self):
            # 多个loop间不共享锁
            loop = asyncio.get_event_loop()
            if self.__map_lock.get(loop, None) is None:
                self.__map_lock[loop] = asyncio.Lock()
            return self.__map_lock[loop]
        pass

    def __init__(self, func_key: Union[Callable, None] = None) -> None:
        self.__func_key = func_key
        print('注解对象初始化')
        pass

    def __call__(self, func_value: Callable) -> Callable:
        print('注解对象调用')
        return (
            MapKey.AsyncLock(self.__func_key)
            if asyncio.iscoroutinefunction(func_value)
            else MapKey.Sync(self.__func_key)(func_value)
        )
    pass
