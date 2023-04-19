import asyncio
from typing import Callable, Union

from .base import AsyncBase
from .func_tool import FqsAsync


class LoopExec:
    """无限循环执行函数
    """
    def __init__(self, func: Callable) -> None:
        self.__func = func
        self.__is_coro = asyncio.iscoroutinefunction(func)
        pass

    async def loop(self, *args, **kwds):
        while True:
            res = self.__func(*args, **kwds)
            if self.__is_coro:
                await res
            pass
    pass


class LoopExecBg:
    """后台无限执行函数
    """
    def __init__(self, exec: LoopExec) -> None:
        self.__exec = exec
        self.__task_main = AsyncBase.get_done_task()
        pass

    @property
    def is_running(self):
        return not self.__task_main.done()

    @property
    def exception(self):
        return self.__task_main.exception() if self.__task_main.done() else None

    def run(self, callback: Union[Callable, None] = None) -> None:
        if not self.__task_main.done():
            raise Exception('已有loop在运行中')
        self.__task_main = AsyncBase.coro2task_exec(self.__exec.loop())

        if callback is not None:
            self.__task_main.add_done_callback(callback)

    def stop(self):
        if not self.__task_main.done():
            self.__task_main.cancel()
        pass
    pass


class NormLoop:
    """在代码块的后台无限执行函数
    """
    def __init__(self, func: Callable, callback: Union[Callable, None] = None) -> None:
        self.__exec_bg = LoopExecBg(LoopExec(func))
        self.__callback = callback
        pass

    def __enter__(self):
        self.__exec_bg.run(self.__callback)
        return self

    def __exit__(self, *args):
        self.__exec_bg.stop()
        pass

    async def __aenter__(self):
        self.__enter__()
        return self

    async def __aexit__(self, *args):
        self.__exit__(*args)
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
        self.__norm_flow.__enter__()
        return self

    async def __aexit__(self, *args):
        self.__norm_flow.__exit__(*args)
        return await FqsAsync.__aexit__(self, *args)
    pass
