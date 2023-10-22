import asyncio

from typing import Any, Callable, Optional, TypeVar
from functools import wraps

from .dict_tool import DictTool


class LockManage:
    def __init__(self) -> None:
        self.__map_lock = dict()
        pass

    def get_lock(self) -> asyncio.Lock:
        loop = asyncio.get_event_loop()
        if self.__map_lock.get(loop) is None:
            self.__map_lock[loop] = asyncio.Lock()
        return self.__map_lock[loop]

    @staticmethod
    def get_for_map(data: dict[Any, 'LockManage'], key) -> 'LockManage':
        if key not in data:
            data[key] = LockManage()
            pass
        return data[key]
    pass


R = TypeVar('R')


class MapKeyBase:
    @staticmethod
    def get_key_sync(func_key: Optional[Callable[..., R]], *args, **kwds) -> R:
        if func_key is None:
            return ''
        return func_key(*args, **kwds)

    @staticmethod
    async def get_key_async(func_key: Optional[Callable[..., R]], *args, **kwds) -> R:
        if func_key is None:
            return ''
        key_res = func_key(*args, **kwds)
        return await key_res if asyncio.iscoroutinefunction(key_res) else key_res
    pass


class MapKeyGlobal:
    class Sync:
        def __init__(self, func_key: Optional[Callable[..., R]]) -> None:
            self.__map: dict[R, Any] = dict()
            self.__func_key = func_key
            pass

        def __call__(self, func_value: Callable[..., R]) -> Callable[..., R]:
            @wraps(func_value)
            def wrapper(*args, **kwds) -> R:
                key = MapKeyBase.get_key_sync(self.__func_key, *args, **kwds)
                if key not in self.__map:
                    self.__map[key] = func_value(*args, **kwds)
                    pass
                return self.__map[key]
            return wrapper
        pass

    class Async:
        def __init__(self, func_key) -> None:
            self.__map = dict()
            self.__func_key = func_key
            self.__lock = LockManage()
            pass

        def __call__(self, func_obj: Callable) -> Callable:
            @wraps(func_obj)
            async def wrapper(*args, **kwds):
                return await self.__wrapper(func_obj, *args, **kwds)
            return wrapper

        async def __wrapper(self, func_obj: Callable, *args, **kwds):
            key = await MapKeyBase.get_key_async(self.__func_key, *args, **kwds)
            if key in self.__map:
                return self.__map[key]

            async with self.__lock.get_lock():
                if key in self.__map:
                    return self.__map[key]
                self.__map[key] = await func_obj(*args, **kwds)
            return self.__map[key]
        pass

    def __init__(self, func_key: Optional[Callable] = None) -> None:
        self.__func_key = func_key
        pass

    def __call__(self, func_obj: R) -> R:
        return (
            MapKeyGlobal.Async(self.__func_key)(func_obj)
            if asyncio.iscoroutinefunction(func_obj)
            else MapKeyGlobal.Sync(self.__func_key)(func_obj)
        )
    pass


class MapKeySelf:
    class Sync:
        def __init__(self, func_key=None) -> None:
            self.__map = dict()
            self.__func_key = func_key
            pass

        def __call__(self, func_obj: Callable[..., R]) -> Callable[..., R]:
            @wraps(func_obj)
            def wrapper(obj, *args, **kwds) -> R:
                key = MapKeyBase.get_key_sync(self.__func_key, obj, *args, **kwds)
                map_now = DictTool.get_value_dict(self.__map, obj)
                if key not in map_now:
                    map_now[key] = func_obj(*args, **kwds)
                return map_now[key]
            return wrapper
        pass

    class Async:
        def __init__(self, func_key=None) -> None:
            self.__map_key = dict()
            self.__func_key = func_key
            self.__map_lock: dict[Any, LockManage] = dict()
            pass

        def __call__(self, func_obj: Callable[..., R]) -> Any:
            @wraps(func_obj)
            async def wrapper(obj, *args, **kwds):
                return await self.__wrapper(func_obj, obj, *args, **kwds)
            return wrapper

        async def __wrapper(self, func_obj: Callable, obj, *args, **kwds):
            key = await MapKeyBase.get_key_async(self.__func_key, obj, *args, **kwds)
            map_now = DictTool.get_value_dict(self.__map_key, obj)
            if key in map_now:
                return map_now[key]

            async with LockManage.get_for_map(self.__map_lock, obj).get_lock():
                if key in map_now:
                    return map_now[key]
                map_now[key] = await func_obj(*args, **kwds)
                pass

            return map_now[key]
        pass

    def __init__(self, func_key=None) -> None:
        self.__func_key = func_key
        pass

    def __call__(self, func_obj: R) -> R:
        return (
            MapKeySelf.Async(self.__func_key)(func_obj)
            if asyncio.iscoroutinefunction(func_obj)
            else MapKeySelf.Sync(self.__func_key)(func_obj)
        )
    pass
