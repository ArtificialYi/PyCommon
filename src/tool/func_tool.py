import asyncio
from typing import Callable
from .base import AsyncBase


class AsyncExecOrder:
    """将可执行对象有序化
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
        res0 = self.__func(*args, **kwds)
        res1 = await res0 if self.__is_coro else res0
        future.set_result(res1)
        self.__queue.task_done()
        return True

    def call(self, *args, **kwds):
        # 业务方使用，成为直接执行的异步函数
        future = AsyncBase.get_future()
        self.__queue.put_nowait((future, args, kwds))
        return future
    pass


class AsyncExecOrderHandle:
    def _func_order(self, func: Callable) -> AsyncExecOrder:
        handle = AsyncExecOrder(func)
        self.__setattr__(func.__name__, handle.call)
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
    def err_no_args():
        raise Exception('会抛出异常的普通函数')
    pass
