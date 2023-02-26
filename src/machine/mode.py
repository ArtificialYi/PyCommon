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
        self.__future_run = AsyncBase.get_future()
        self.__graph = graph
        self.__fq_order: AsyncExecOrder = graph.fq_order if fq_order is None else fq_order
        self.__lock = asyncio.Lock()
        pass

    @property
    def is_running(self):
        return self.__future_run.done()

    async def __no_sign(self):
        func = self.__graph.func_get()
        # 运行时状态存在为None才可能触发
        if func is None:
            return await self.__fq_order.queue_wait()
        res_pre = func()
        return await res_pre if asyncio.iscoroutinefunction(func) else res_pre

    def __running_err(self):
        if self.is_running:
            raise Exception('已有loop在运行中')

    async def __main(self):
        self.__future_run.set_result(True)
        while self.__graph.status != self.__graph.status_exited:
            if await self.__fq_order.queue_no_wait():
                continue
            await self.__no_sign()
            pass
        self.__future_run = AsyncBase.get_future()
        pass

    async def run_async(self) -> asyncio.Future:
        async with self.__lock:
            self.__running_err()
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
        self.__graph = SGMachineForFlow(SGForFlow(func))
        self.__sign_deal = ActionGraphSign(self.__graph)
        pass

    async def __aenter__(self):
        if self.__graph.status != self.__graph.status_exited:
            raise Exception(f'状态机启动失败|status:{self.__graph.status}')
        await self.__graph.status_change(SGForFlow.State.STARTED)
        await self.__graph.__aenter__()
        await self.__sign_deal.run_async()
        return self

    async def __aexit__(self, *args):
        # 将状态转移至exited
        if not self.__sign_deal.is_running:
            raise Exception('状态机尚未启动')
        await self.__graph.status_change(self.__graph.status_exited)
        await self.__graph.__aexit__(*args)
        pass
    pass


class DeadWaitFlow(FqsAsync):
    """基于基本状态机的异步API流
    依赖与逻辑链路
    1. 将普通函数 转化为 队列函数
    2. 将队列函数开放

    1. 清空死等队列后再exit
    """
    def __init__(self, func: Callable) -> None:
        super().__init__(func)
        self.__flow = NormFlow(self.fq_order.queue_wait)
        pass

    @property
    def qsize(self):
        return self.fq_order.qsize

    async def qjoin(self):
        return await self.fq_order.queue_join()

    async def __aenter__(self):
        await super().__aenter__()
        return await self.__flow.__aenter__()

    async def __aexit__(self, *args):
        await self.fq_order.call_step()
        await self.__flow.__aexit__(*args)
        await super().__aexit__(*args)
        pass
    pass
