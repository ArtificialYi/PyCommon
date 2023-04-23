import asyncio
from typing import Callable, Union

from ..exception.tool import AlreadyStopException
from .map_tool import LockManage
from .base import AsyncBase
from .func_tool import FqsAsync, FuncTool


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

    @property
    def is_running(self):
        return not self.__task_main.done()

    def run(self, callback: Union[Callable, None] = None) -> None:
        if not self.__task_main.done():
            raise Exception('已有loop在运行中')
        self.__task_main = AsyncBase.coro2task_exec(self.__exec.loop())

        if callback is not None:
            self.__task_main.add_done_callback(callback)

    async def stop(self):
        """
        1. 未停止 => 任务取消 & 获取任务结果 => 非取消结果则抛出异常
        2. 已取消的任务 => 逻辑错误 => 抛出异常
        """
        task = self.__task_main
        if task.cancelled():
            raise AlreadyStopException('loop早已正常停止, 无法再次停止')

        await self.__task_cancel(task)
        pass

    async def __task_cancel(self, task: asyncio.Task):
        async with self.__task_lock.get_lock():
            if task.cancelled():
                raise AlreadyStopException('loop早已正常停止, 无法再次停止')
            if not task.done():
                task.cancel()
                await FuncTool.await_no_cancel(task)
                pass
            pass
        pass
    pass


class NormLoop:
    """在代码块的后台无限执行函数
    """
    def __init__(self, func: Callable, callback: Union[Callable, None] = None) -> None:
        self.__exec_bg = LoopExecBg(func)
        self.__callback = callback
        pass

    async def __aenter__(self):
        self.__exec_bg.run(self.__callback)
        return self

    async def __aexit__(self, *args):
        await self.__exec_bg.stop()
        pass
    pass


class OrderApi(FqsAsync):
    """函数 -> 有序执行
    """
    def __init__(self, func: Callable, callback: Union[Callable, None] = None) -> None:
        FqsAsync.__init__(self, func)
        self.__norm_flow = NormLoop(self.fq_order.queue_wait, callback)
        pass

    async def __aenter__(self):
        await FqsAsync.__aenter__(self)
        await self.__norm_flow.__aenter__()
        return self

    async def __aexit__(self, *args):
        await self.__norm_flow.__aexit__(*args)
        return await FqsAsync.__aexit__(self, *args)
    pass
