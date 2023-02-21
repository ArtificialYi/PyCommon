import asyncio
from functools import wraps
import threading
from typing import Callable, Union
from .base import AsyncBase
import pytest


# class RaiseLoopErr:
#     @staticmethod
#     def raise_err(re: RuntimeError):
#         if re.args[0] != 'Event loop is closed':
#             raise re
#         pass
#     pass


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

    async def __queue_func(self, future: Union[asyncio.Future, None], *args, **kwds):
        if future is None:
            return False
        res0 = self.__func(*args, **kwds)
        res1 = await res0 if self.__is_coro else res0
        future.set_result(res1)
        return True

    async def queue_no_wait(self):
        # 队列拥有者使用，消费队列
        if self.__queue.qsize() == 0:
            return False
        return await self.queue_wait()

    async def queue_wait(self):
        future, args, kwds = await self.__queue.get()
        res = await self.__queue_func(future, *args, **kwds)
        self.__queue.task_done()
        return res

    async def queue_join(self):
        return await self.__queue.join()

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


class FuncTool:
    @staticmethod
    async def is_async_err(func: Callable):
        try:
            await func()
        except Exception:
            return True
        else:
            return False

    @staticmethod
    def is_func_err(func: Callable, *args, **kwds):
        """函数有错误
        """
        try:
            func(*args, **kwds)
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


class LockThread:
    def __new__(cls, func: Callable) -> Callable:
        lock = threading.Lock()

        @wraps(func)
        def func_lock(*args, **kwds):
            with lock:
                return func(*args, **kwds)
        return func_lock
    pass


class PytestAsyncTimeout:
    def __init__(self, t: int) -> None:
        self.__time = t
        # self.__delay = 0
        pass

    def __call__(self, func: Callable):
        @pytest.mark.timeout(self.__time)
        @pytest.mark.asyncio
        @wraps(func)
        async def func_pytest(*args, **kwds):
            return await func(*args, **kwds)
        return func_pytest
    pass


class CallableDecoratorAsync:
    def __init__(self, func: Callable) -> None:
        if not asyncio.iscoroutinefunction(func):
            raise Exception(f'函数类型错误:{func}')

        self.__func_async = func
        pass

    def __call__(self, func: Callable):
        if not asyncio.iscoroutinefunction(func):
            raise Exception(f'函数类型错误:{func}')

        @wraps(func)
        async def func_async(obj, *args, **kwds):
            return await self.__func_async(func, obj, *args, **kwds)
        return func_async
    pass


class FieldSwap(object):
    """暂时替换对象中的某个属性
    """
    def __init__(self, obj, field, value) -> None:
        self.__obj = obj
        self.__field = field
        self.__tmp = getattr(obj, field)
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
    2. 多线程也仅能替换一次
    """
    def __init__(self, obj, field, value) -> None:
        super().__init__(obj, field, value)
        self.__lock_async = asyncio.Lock()
        self.__lock_sync = threading.Lock()
        pass

    def __enter__(self):
        self.__lock_sync.__enter__()
        return FieldSwap.__enter__(self)

    def __exit__(self, *args):
        FieldSwap.__exit__(self, *args)
        self.__lock_sync.__exit__(*args)

    async def __aenter__(self):
        await self.__lock_async.__aenter__()
        return await FieldSwap.__aenter__(self)

    async def __aexit__(self, *args):
        await FieldSwap.__aexit__(self, *args)
        await self.__lock_async.__aexit__(*args)
    pass


class FQSSync(FieldSwapSafe):
    """函数队列的基类
    Func Queue Safe
    """
    def __init__(self, func: Callable) -> None:
        self.__fq_order = AsyncExecOrder(func)
        super().__init__(self, func.__name__, self.__fq_order.call_sync)
        pass

    @property
    def fq_order(self):
        return self.__fq_order
    pass


class FQSAsync(FieldSwapSafe):
    """函数队列的基类
    Func Queue Safe
    """
    def __init__(self, func: Callable) -> None:
        self.__fq_order = AsyncExecOrder(func)
        super().__init__(self, func.__name__, self.__fq_order.call_async)
        pass

    @property
    def fq_order(self):
        return self.__fq_order
    pass
