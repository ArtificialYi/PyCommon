import asyncio
from collections import deque
from typing import Awaitable, Iterable


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
        return type(obj) is int

    @staticmethod
    def istrue(obj):
        return type(obj) is bool and obj

    @staticmethod
    def to_str(obj):
        if type(obj) is str:
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


class AsyncBase:
    @staticmethod
    def get_future():
        return asyncio.get_running_loop().create_future()

    @staticmethod
    def get_done_task() -> asyncio.Task:
        future = AsyncBase.get_future()
        future.cancel()
        return asyncio.ensure_future(future)

    @staticmethod
    def call_later(delay, func, *args, **kwds):
        return asyncio.get_running_loop().call_later(delay, func, *args, **kwds)

    @staticmethod
    async def wait_done(task: Awaitable, timeout: float):
        done, _ = await asyncio.wait({task}, timeout=timeout)
        return task in done
    pass
