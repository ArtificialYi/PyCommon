import asyncio
from typing import Callable
from .base import AsyncBase


class AsyncExecOrder:
    """将可执行对象有序化-可执行对象的生命周期将会与loop绑定
    1. 函数与Queue绑定，Queue与loop绑定-无法更改
    3. 如果loop被close，则当前对象常规使用会抛出异常
    """
    def __init__(self, func: Callable) -> None:
        self.__queue = asyncio.Queue()
        self.__func = func
        self.__is_coro = asyncio.iscoroutinefunction(func)
        pass

    @property
    def qsize(self):
        return self.__queue.qsize()

    async def queue_no_wait(self):
        # 队列拥有者使用，消费队列
        if self.__queue.qsize() == 0:
            return False
        return await self.queue_wait()

    async def queue_wait(self):
        # 队列拥有者使用，消费队列
        future, args, kwds = await self.__queue.get()
        self.__queue.task_done()
        if future is None:
            return True
        res0 = self.__func(*args, **kwds)
        res1 = await res0 if self.__is_coro else res0
        future.set_result(res1)
        return True

    async def call_step(self, *args, **kwds):
        return await self.__queue.put((None, args, kwds))

    async def call_sync(self, *args, **kwds):
        # 同步调用，返回函数常规返回值
        future = await self.call_async(*args, **kwds)
        return await future

    async def call_async(self, *args, **kwds):
        # 异步调用，返回一个future
        future = AsyncBase.get_future()
        await self.__queue.put((future, args, kwds))
        return future
    pass


class AsyncExecOrderHandle:
    def _func_sync(self, func: Callable) -> AsyncExecOrder:
        handle = AsyncExecOrder(func)
        self.__setattr__(func.__name__, handle.call_sync)
        return handle

    def _func_async(self, func: Callable) -> AsyncExecOrder:
        handle = AsyncExecOrder(func)
        self.__setattr__(func.__name__, handle.call_async)
        return handle
    pass


class FuncTool:
    @staticmethod
    async def is_func_err(func: Callable):
        """函数有错误
        """
        try:
            res = func()
            await res if asyncio.iscoroutinefunction(func) else res
        except Exception:
            return True
        else:
            return False

    @staticmethod
    async def norm_async_err():
        raise Exception('会抛出异常的coro函数')

    @staticmethod
    def norm_sync_err():
        raise Exception('会抛出异常的普通函数')

    @staticmethod
    async def norm_async():
        pass

    @staticmethod
    def norm_sync():
        pass
    pass
