import asyncio
from collections import deque
from typing import Any, Callable, Dict, Iterable, Optional


class BaseTool:
    @staticmethod
    def return_self(obj):
        return obj

    @staticmethod
    def all_none_iter(obj: Iterable):
        for item in obj:
            if item is None:
                continue
            return False
        return True

    @staticmethod
    def isint(obj):
        return type(obj) == int

    @staticmethod
    def istrue(obj):
        return type(obj) == bool and obj

    @staticmethod
    def to_str(obj):
        if type(obj) == str:
            return obj
        return str(obj)

    @staticmethod
    def isnone(obj):
        return obj is None
    pass


class DelayCountQueue:
    """延迟统计队列
    1. 只有在真正有值时才创建
    """
    def __init__(self, num: float, max_len: int = 1000) -> None:
        self.__deque_sum = deque(maxlen=max_len + 1)
        self.__sum = 0

        self.newest = 0
        self.newest = num
        pass

    @property
    def newest(self) -> float:
        return self.__new

    @newest.setter
    def newest(self, num):
        self.__new = num
        self.__sum += num
        self.__deque_sum.append(self.__sum)
        pass

    @property
    def average(self):
        return (self.__deque_sum[-1] - self.__deque_sum[0]) / (len(self.__deque_sum) - 1)
    pass


class MatchCase:
    def __init__(self, case_dict: Dict[Any, Optional[Callable]], default: Optional[Callable] = None) -> None:
        self.__case_dict = case_dict
        self.__case_set = set(self.__case_dict.keys())
        self.__default = default if default is not None else self.__err_default
        pass

    async def match(self, key, *args, **kwds):
        if key not in self.__case_set:
            return await self.__default(key, *args, **kwds)
        coro = self.__case_dict[key]
        if coro is None:
            return
        return await coro(*args, **kwds)

    async def __err_default(self, key, *args, **kwds):
        raise Exception(f'{self}未知{key}异常:{args}|{kwds}')
    pass


class AsyncBase:
    @staticmethod
    def get_future():
        return asyncio.get_running_loop().create_future()

    @staticmethod
    def coro2task_exec(coro):
        return asyncio.get_running_loop().create_task(coro)

    @staticmethod
    def get_done_task() -> asyncio.Task:
        future = asyncio.get_event_loop().create_future()
        future.cancel()
        return asyncio.ensure_future(future)
    pass
