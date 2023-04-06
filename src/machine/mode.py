import asyncio
from typing import Callable, Union

from ..tool.base import AsyncBase
from .status import SGForFlow, SGMachineForFlow
from ..tool.func_tool import AsyncExecOrder, FqsAsync


class ActionGraphSign:
    """状态图的队列信号操作逻辑
    1. 有队列信号时 处理 函数队列（函数队列如果是状态图的状态转换则为普通流）
    2. 无队列信号时 处理 状态图运行时
        1. 运行时有函数时 无限调用 函数
        2. 运行时没有函数时 等待 队列信号

    lock:
    1. 协程内多个main同时运行将会出错
    """
    def __init__(self, graph: SGMachineForFlow, fq_order: Union[AsyncExecOrder, None] = None) -> None:
        self.__graph = graph
        self.__fq_order: AsyncExecOrder = graph.fq_order if fq_order is None else fq_order
        self.__task_main: Union[asyncio.Task, None] = None
        pass

    @property
    def is_running(self):
        return self.__task_main is not None and not self.__task_main.done()

    @property
    def exception(self):
        return self.__task_main.exception() if self.__task_main is not None and self.__task_main.done() else None

    async def __no_sign(self):
        func = self.__graph.func_get()
        # 运行时状态存在为None才可能触发
        if func is None:
            return await self.__fq_order.queue_wait()
        res_pre = func()
        return await res_pre if asyncio.iscoroutinefunction(func) else res_pre

    async def __main(self):
        while self.__graph.status != self.__graph.status_exited:
            if await self.__fq_order.queue_no_wait():
                continue
            await self.__no_sign()
            pass
        pass

    def run_async(self) -> None:
        if self.is_running:
            raise Exception('已有loop在运行中')
        self.__task_main = AsyncBase.coro2task_exec(self.__main())
    pass


class NormFlow:
    """基于基本状态机的普通流
    1. 普通函数的状态图
    2. 状态转移 函数 <=> 队列
    3. 队列信号操作逻辑
    """
    def __init__(self, func: Callable) -> None:
        self.__graph = SGMachineForFlow(SGForFlow(func))
        self.__sign_deal = ActionGraphSign(self.__graph)
        pass

    @property
    def exception(self):
        return self.__sign_deal.exception

    async def __aenter__(self):
        """
        1. 同步启动会报错
        2. 并发启动会报错
        """
        # 做好流启动准备
        if self.__graph.status != self.__graph.status_exited:
            raise Exception(f'状态机启动失败|status:{self.__graph.status}')
        await self.__graph.status_change(SGForFlow.State.STARTED)
        # 状态机开始接收状态转移信号（默认为关闭信号）
        await self.__graph.__aenter__()
        # 状态机启动，开始处理状态转移信号 & func
        self.__sign_deal.run_async()
        return self

    async def __aexit__(self, *args):
        e = (
            None if self.__sign_deal.is_running
            else Exception('状态机尚未启动') if self.__sign_deal.exception is None else self.__sign_deal.exception
        )
        # 强行关闭状态机
        args = (None, None, None) if e is None else (None, e, None)
        await self.__graph.__aexit__(*args)
        await self.__graph.status_change(self.__graph.status_exited)
    pass


class DeadWaitFlow(FqsAsync):
    """基于基本状态机的异步API流
    依赖与逻辑链路
    1. 将普通函数 转化为 队列函数
    2. 将队列函数开放

    1. 清空死等队列后再exit
    """
    def __init__(self, func: Callable) -> None:
        FqsAsync.__init__(self, func)
        self.__flow = NormFlow(self.fq_order.queue_wait)
        pass

    @property
    def qsize(self):
        return self.fq_order.qsize

    @property
    def exception(self):
        return self.__flow.exception

    async def qjoin(self):
        return await self.fq_order.queue_join()

    async def __aenter__(self):
        # 状态机启动，开始处理函数队列
        await self.__flow.__aenter__()
        # 开始接收函数调用
        await FqsAsync.__aenter__(self)
        return self

    async def __aexit__(self, *args):
        # 关闭接收外部函数队列调用（函数可以直接调用）
        await FqsAsync.__aexit__(self, *args)
        # 发送一个空信号给函数队列
        await self.fq_order.call_step()
        # 状态机尝试关闭
        await self.__flow.__aexit__(*args)
        pass
    pass
