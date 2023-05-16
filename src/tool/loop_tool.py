import asyncio
from concurrent.futures import ALL_COMPLETED
from typing import Callable

from ..exception.tool import AlreadyRunException
from .base import AsyncBase
from .func_tool import FqsAsync


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
        pass

    @property
    def task(self):
        return self.__task_main

    def run(self):
        if not self.__task_main.done():
            raise AlreadyRunException('已有loop在运行中')
        self.__task_main = asyncio.create_task(self.__exec.loop())
        return self

    async def stop(self):
        self.__task_main.cancel()
        await asyncio.wait({self.__task_main}, return_when=ALL_COMPLETED)
        pass
    pass


class NormLoop:
    """在代码块的后台无限执行函数
    """
    def __init__(self, func: Callable) -> None:
        self.__exec_bg = LoopExecBg(func)
        pass

    @property
    def task(self):
        return self.__exec_bg.task

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

    @property
    def task(self):
        return self.__norm_flow.task

    async def __aenter__(self):
        await FqsAsync.__aenter__(self)
        await self.__norm_flow.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.__norm_flow.__aexit__(*args)
        await FqsAsync.__aexit__(self, *args)
    pass
