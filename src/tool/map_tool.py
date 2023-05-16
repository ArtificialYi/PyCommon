import asyncio
from functools import wraps
from typing import Callable, Optional


class LockManage:
    def __init__(self) -> None:
        self.__map_lock = dict()
        pass

    def get_lock(self) -> asyncio.Lock:
        loop = asyncio.get_event_loop()
        if self.__map_lock.get(loop) is None:
            self.__map_lock[loop] = asyncio.Lock()
        return self.__map_lock[loop]
    pass


class MapKey:
    class Sync:
        def __init__(self, func_key: Optional[Callable] = None) -> None:
            self.__map = dict()
            self.__func_key = func_key
            pass

        def __call__(self, func_value: Callable) -> Callable:
            @wraps(func_value)
            def wrapper(*args, **kwds):
                key = self.__get_key(*args, **kwds)
                if self.__map.get(key) is None:
                    self.__map[key] = func_value(*args, **kwds)
                return self.__map[key]
            return wrapper

        def __get_key(self, *args, **kwds):
            if self.__func_key is None:
                return ''
            return self.__func_key(*args, **kwds)
        pass

    class AsyncLock:
        def __init__(self, func_key: Optional[Callable]) -> None:
            self.__map = dict()
            self.__func_key = func_key
            self.__iscoro = asyncio.iscoroutinefunction(func_key)
            self.__lock = LockManage()
            pass

        def __call__(self, func_value: Callable) -> Callable:
            @wraps(func_value)
            async def wrapper(*args, **kwds):
                return await self.__wrapper(func_value, *args, **kwds)
            return wrapper

        async def __wrapper(self, func_value: Callable, *args, **kwds):
            key = await self.__get_key(*args, **kwds)
            if self.__map.get(key) is not None:
                return self.__map[key]

            async with self.__lock.get_lock():
                if self.__map.get(key) is not None:
                    return self.__map[key]
                self.__map[key] = await func_value(*args, **kwds)
            return self.__map[key]

        async def __get_key(self, *args, **kwds):
            if self.__func_key is None:
                return ''
            key_res = self.__func_key(*args, **kwds)
            return await key_res if self.__iscoro else key_res
        pass

    def __init__(self, func_key: Optional[Callable] = None) -> None:
        self.__func_key = func_key
        print(f'MapKey初始化:{func_key.__name__ if func_key is not None else func_key}')
        pass

    def __call__(self, func_value: Callable) -> Callable:
        print(f'MapKey调用:{func_value.__name__}')
        return (
            MapKey.AsyncLock(self.__func_key)(func_value)
            if asyncio.iscoroutinefunction(func_value)
            else MapKey.Sync(self.__func_key)(func_value)
        )
    pass
