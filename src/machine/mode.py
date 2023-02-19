import asyncio
from typing import Callable

from ..tool.base import AsyncBase
from .status import NormStatusGraph
from ..tool.func_tool import Func2CallableOrderAsync, Func2CallableOrderSync


class GraphSignDealMachine:
    """基于状态图的基本状态机
    信号处理loop-生命周期与loop一致
    1. 有信号时处理状态转换
    2. 无信号时处理状态运行时
    """
    def __init__(self, graph: NormStatusGraph) -> None:
        self.__graph = graph
        self.__future_run = AsyncBase.get_future()
        self.__lock = asyncio.Lock()
        # 封装和替换
        self.__handle_sign = Func2CallableOrderSync(self, self.sign_deal)
        pass

    @property
    def future_run(self):
        return self.__future_run

    async def sign_deal(self, status_target, *args, **kwds):
        # 所有状态转移均在此处处理
        func = self.__graph.func_get_target(status_target)
        if func is None:
            return None
        res = func(*args, **kwds)
        return await res if asyncio.iscoroutinefunction(func) else res

    async def __no_sign(self):
        func = self.__graph.func_get()
        if func is None:
            return await self.__handle_sign.queue_wait()
        res_pre = func()
        return await res_pre if asyncio.iscoroutinefunction(func) else res_pre

    async def main(self):
        self.__running_err()
        async with self.__lock:
            self.__future_run.set_result(True)
            while self.__graph.status != self.__graph.status_exited:
                if await self.__handle_sign.queue_no_wait():
                    continue
                await self.__no_sign()
                pass
            self.__future_run = AsyncBase.get_future()
            pass
        pass

    def __running_err(self):
        if self.__future_run.done():
            raise Exception('已有loop在运行中')
    pass


class NormFlow:
    """基于基本状态机的普通流
    """
    def __init__(self, graph: NormStatusGraph) -> None:
        self.__graph = graph
        self.__machine = GraphSignDealMachine(graph)
        pass

    async def __launch(self):
        # 开启状态流的loop-同时只能启动一个loop & 状态不处于exited
        if self.__machine.future_run.done() or self.__graph.status != self.__graph.status_exited:
            raise Exception(f'状态机启动失败|status:{self.__graph.status}|run:{self.__machine.future_run.done()}')
        self.__graph.start()
        return await self.__machine.main()

    async def __aenter__(self):
        AsyncBase.coro2task_exec(self.__launch())
        await self.__machine.future_run
        return self

    async def __aexit__(self, *args):
        # 将状态转移至exited
        if not self.__machine.future_run.done():
            raise Exception('状态机尚未启动')
        return await self.__machine.sign_deal(self.__graph.status_exited)
    pass


class DeadWaitFlow(NormFlow):
    """以死等的方式调用func
    依赖与逻辑链路
    1. 流 拥有 func => 队列函数A => 逻辑B 逻辑C 函数属性
    2. 流 仅对外开放func
    2. 逻辑B => 状态图构造时
    2. 逻辑C => 流运行时 => 流自带逻辑C
    3. 函数属性 => 流运行时

    1. 清空死等队列后再exit
    """
    def __init__(self, func: Callable) -> None:
        self.__call_order = Func2CallableOrderAsync(self, func)
        NormFlow.__init__(self, NormStatusGraph(self.__call_order.queue_wait))
        pass

    @property
    def qsize(self):
        return self.__call_order.qsize

    async def qjoin(self):
        return await self.__call_order.queue_join()

    async def __aexit__(self, *args):
        await self.__call_order.call_step()
        return await super().__aexit__(*args)
    pass
