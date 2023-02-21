import asyncio
from typing import Callable

from ..tool.base import AsyncBase
from .status import NormStatusGraph
from ..tool.func_tool import AsyncExecOrder, FQSAsync, FQSSync


class FQSStatusChange(FQSSync):
    """状态图外置函数队列
    """
    def __init__(self, graph: NormStatusGraph) -> None:
        self.__graph = graph
        super().__init__(self.status_change)
        pass

    async def status_change(self, status_target, *args, **kwds):
        # 所有状态转移均在此处处理
        func = self.__graph.func_get_target(status_target)
        if func is None:
            return None
        res = func(*args, **kwds)
        return await res if asyncio.iscoroutinefunction(func) else res
    pass


class ActionGraphSign:
    """状态图的队列信号操作逻辑
    1. 有队列信号时 处理 函数队列（函数队列如果是状态转换则为普通流）
    2. 无队列信号时 处理 状态图运行时
        1. 运行时有函数时 无限调用 函数
        2. 运行时没有函数时 等待 队列信号

    lock:
    1. 协程内多个main同时运行将会出错
    """
    def __init__(self, graph: NormStatusGraph, fq_order: AsyncExecOrder) -> None:
        self.__future_run = AsyncBase.get_future()
        self.__graph = graph
        self.__fq_order = fq_order
        pass

    @property
    def is_running(self):
        return self.__future_run.done()

    async def __no_sign(self):
        func = self.__graph.func_get()
        if func is None:
            return await self.__fq_order.queue_wait()
        res_pre = func()
        return await res_pre if asyncio.iscoroutinefunction(func) else res_pre

    def __running_err(self):
        if self.is_running:
            raise Exception('已有loop在运行中')

    async def __main(self):
        self.__running_err()
        self.__future_run.set_result(True)
        while self.__graph.status != self.__graph.status_exited:
            if await self.__fq_order.queue_no_wait():
                continue
            await self.__no_sign()
            pass
        self.__future_run = AsyncBase.get_future()
        pass

    async def run_async(self) -> asyncio.Future:
        AsyncBase.coro2task_exec(self.__main())
        return await self.__future_run
    pass


class NormFlow:
    """基于基本状态机的普通流
    1. 普通函数的状态图
    2. 状态转移 函数 <=> 队列
    3. 队列信号操作逻辑
    """
    def __init__(self, func: Callable) -> None:
        self.__graph = NormStatusGraph(func)
        self.__fq_status_change = FQSStatusChange(self.__graph)
        self.__sign_deal = ActionGraphSign(self.__graph, self.__fq_status_change.fq_order)
        pass

    async def __aenter__(self):
        await self.__fq_status_change.__aenter__()
        if self.__graph.status != self.__graph.status_exited:
            raise Exception(f'状态机启动失败|status:{self.__graph.status}')
        self.__graph.start()
        await self.__sign_deal.run_async()
        return self

    async def __aexit__(self, *args):
        # 将状态转移至exited
        if not self.__sign_deal.is_running:
            raise Exception('状态机尚未启动')
        await self.__fq_status_change.status_change(self.__graph.status_exited)
        await self.__fq_status_change.__aexit__(*args)
        pass
    pass


class DeadWaitFlow(NormFlow):
    """基于基本状态机的异步API流
    依赖与逻辑链路
    1. 将普通函数 转化为 队列函数
    2. 将队列函数开放

    1. 清空死等队列后再exit
    """
    def __init__(self, func: Callable) -> None:
        self.__fq = FQSAsync(func)
        NormFlow.__init__(self, self.__fq.fq_order.queue_wait)
        pass

    @property
    def qsize(self):
        return self.__fq.fq_order.qsize

    async def qjoin(self):
        return await self.__fq.fq_order.queue_join()

    async def __aenter__(self):
        await self.__fq.__aenter__()
        return await NormFlow.__aenter__(self)

    async def __aexit__(self, *args):
        await self.__fq.fq_order.call_step()
        await NormFlow.__aexit__(self, *args)
        await self.__fq.__aexit__(self, *args)
        pass
    pass
