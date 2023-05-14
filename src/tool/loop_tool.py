import asyncio
from typing import Callable

from ..exception.tool import AlreadyStopException
from .map_tool import LockManage
from .base import AsyncBase
from .func_tool import FqsAsync, FqsSync, TqsAsync


class LoopExec:
    """无限循环执行函数
    """
    def __init__(self, func: Callable) -> None:
        self.__func = func
        pass

    async def loop(self, *args, **kwds):
        while True:
            await self.__func(*args, **kwds)
    pass


class LoopExecBg:
    """后台无限执行函数
    """
    def __init__(self, func: Callable) -> None:
        self.__exec = LoopExec(func)
        self.__task_main = AsyncBase.get_done_task()
        self.__task_lock = LockManage()
        pass

    def __await__(self):
        return (yield from self.__task_main)

    def run(self) -> None:
        if not self.__task_main.done():
            raise Exception('已有loop在运行中')
        self.__task_main = AsyncBase.coro2task_exec(self.__exec.loop())
        pass

    async def __task_cancel(self, task: asyncio.Task):
        async with self.__task_lock.get_lock():
            if task.cancelled():
                raise AlreadyStopException('loop早已正常停止, 无法再次停止')
            if not task.done():
                task.cancel()
                pass
            await asyncio.sleep(0.1)
            pass
        pass

    async def __stop(self):
        if self.__task_main.cancelled():
            raise AlreadyStopException('loop早已正常停止, 无法再次停止')
        await self.__task_cancel(self.__task_main)

    async def stop(self):
        try:
            await self.__stop()
        except asyncio.CancelledError:
            self.__task_main.cancel()
            await self.__task_main
            raise
        pass
    pass


class NormLoop:
    """在代码块的后台无限执行函数
    """
    def __init__(self, func: Callable) -> None:
        self.__exec_bg = LoopExecBg(func)
        pass

    def __await__(self):
        yield from self.__exec_bg.__await__()
        pass

    async def __aenter__(self):
        self.__exec_bg.run()
        return self

    async def __aexit__(self, *args):
        await self.__exec_bg.stop()
        pass
    pass


class OrderApi(FqsAsync):
    """函数 -> 有序队列执行
    """
    def __init__(self, func: Callable) -> None:
        FqsAsync.__init__(self, func)
        self.__norm_flow = NormLoop(self.fq_order.queue_wait)
        pass

    def __await__(self):
        yield from self.__norm_flow.__await__()

    async def __aenter__(self):
        await FqsAsync.__aenter__(self)
        await self.__norm_flow.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.__norm_flow.__aexit__(*args)
        return await FqsAsync.__aexit__(self, *args)
    pass


class OrderApiSync(FqsSync):
    """函数 -> 有序队列执行
    """
    def __init__(self, func: Callable) -> None:
        FqsSync.__init__(self, func)
        self.__norm_flow = NormLoop(self.fq_order.queue_wait)
        pass

    def __await__(self):
        yield from self.__norm_flow.__await__()

    async def __aenter__(self):
        await FqsSync.__aenter__(self)
        await self.__norm_flow.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.__norm_flow.__aexit__(*args)
        return await FqsSync.__aexit__(self, *args)
    pass


class TaskApi(TqsAsync):
    """函数 -> 任务队列执行
    """
    def __init__(self, func: Callable, timeout: float = 1) -> None:
        TqsAsync.__init__(self, func, timeout)
        self.__norm_flow = NormLoop(self.tq_order.queue_wait)
        pass

    def __await__(self):
        yield from self.__norm_flow.__await__()

    async def __aenter__(self):
        await TqsAsync.__aenter__(self)
        await self.__norm_flow.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.__norm_flow.__aexit__(*args)
        return await TqsAsync.__aexit__(self, *args)
    pass
