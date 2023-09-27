import asyncio
from functools import wraps
import threading
from typing import Callable, Tuple, TypeVar

from .base import AsyncBase


class AsyncExecOrder:
    """将可执行对象有序化-可执行对象的生命周期将会与loop绑定
    1. 函数与Queue绑定，Queue与loop绑定-无法更改
    3. 如果loop被close，则当前对象常规使用会抛出异常
    """
    def __init__(self, func: Callable) -> None:
        self.__queue: asyncio.Queue[Tuple[asyncio.Future, tuple, dict]] = asyncio.Queue()
        self.__func = func
        self.__is_coro = asyncio.iscoroutinefunction(func)
        pass

    @property
    def qsize(self):
        return self.__queue.qsize()

    async def __queue_func(self, *args, **kwds):
        res0 = self.__func(*args, **kwds)
        return await res0 if self.__is_coro else res0

    async def queue_wait(self):
        future, args, kwds = await self.__queue.get()
        res = await self.__queue_func(*args, **kwds)
        future.set_result(res)
        self.__queue.task_done()
        return res

    async def call_async(self, *args, **kwds):
        # 异步调用，返回一个future
        future = AsyncBase.get_future()
        await self.__queue.put((future, args, kwds))
        return future
    pass


class ExceptTool:
    @staticmethod
    def raise_not_exception(e: BaseException):
        if not isinstance(e, Exception):
            raise
    pass


R = TypeVar('R')


def lock_thread(func: Callable[..., R]) -> Callable[..., R]:
    lock = threading.Lock()

    @wraps(func)
    def func_lock(*args, **kwds):
        with lock:
            return func(*args, **kwds)
    return func_lock


class FieldSwap(object):
    """暂时替换对象中的某个属性
    """
    def __init__(self, obj, field, value) -> None:
        self.__obj = obj
        self.__field = field
        self.__tmp = getattr(obj, field, None)
        self.__value = value
        pass

    def __enter__(self):
        setattr(self.__obj, self.__field, self.__value)
        return self

    async def __aenter__(self):
        setattr(self.__obj, self.__field, self.__value)
        return self

    def __exit__(self, *args):
        setattr(self.__obj, self.__field, self.__tmp)
        pass

    async def __aexit__(self, *args):
        setattr(self.__obj, self.__field, self.__tmp)
        pass
    pass


class FieldSwapSafe(FieldSwap):
    """为属性替换加上协程锁 & 线程锁
    1. 协程内仅能替换一次
    """
    def __init__(self, obj, field, value) -> None:
        super().__init__(obj, field, value)
        self.__lock_async = asyncio.Lock()
        pass

    async def __aenter__(self):
        await self.__lock_async.__aenter__()
        return await FieldSwap.__aenter__(self)

    async def __aexit__(self, *args):
        await FieldSwap.__aexit__(self, *args)
        await self.__lock_async.__aexit__(*args)
        pass
    pass


class FqsAsync(FieldSwapSafe):
    """函数队列的基类
    Func Queue Safe
    """
    def __init__(self, func: Callable) -> None:
        self.__fq_order = AsyncExecOrder(func)
        super().__init__(self, func.__name__, self.__fq_order.call_async)
        pass

    @property
    def fq_order(self) -> AsyncExecOrder:
        return self.__fq_order
    pass
