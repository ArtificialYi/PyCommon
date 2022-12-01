import asyncio
from typing import Callable, Union
from .status import StatusValue, StatusGraph, StatusEdge
from enum import Enum, auto
# from ..tool.base import AsyncBase, MatchCase
from ..tool.func_tool import CallableOrder
# from .queue import NormManageQueue


class StatusGraphBase:
    def __init__(self) -> None:
        self._status = None
        self.__status_graph: StatusGraph = self._graph_build()
        pass

    def status2target(self, status):
        self._status = status
        pass

    def _graph_build(self) -> StatusGraph:
        """
        状态转移方程式
        需要子类重写
        """
        raise Exception('子类需要重写这个函数')

    def func_get(self) -> Union[Callable, None]:
        value = self.__status_graph.get(self._status, self._status)
        return value.func if value is not None else None

    def func_get_target(self, status) -> Union[Callable, None]:
        value = self.__status_graph. get(self._status, status)
        return value.func if value is not None else None
    pass


class NormStatusGraph(StatusGraphBase):
    """普通的状态图
    """
    class State(Enum):
        STARTED = auto()
        STOPPED = auto()
        EXITED = auto()
        pass

    def __init__(self) -> None:
        """状态机的初始应该是EXITED状态
        1. 从EXITED状态到其他状态应该由loop管理者控制(因为EXITED状态会退出loop)
        2. 其他状态之间的变化由状态机控制
        """
        StatusGraphBase.__init__(self)
        self.status2target(NormStatusGraph.State.EXITED)
        pass

    def _graph_build(self):
        graph_tmp = StatusGraph()
        graph_tmp.add(
            StatusEdge(NormStatusGraph.State.STOPPED, NormStatusGraph.State.STARTED),
            StatusValue(self.__start)
        )
        graph_tmp.add(
            StatusEdge(NormStatusGraph.State.STARTED, NormStatusGraph.State.STARTED),
            StatusValue(self._starting)
        )
        graph_tmp.add(
            StatusEdge(NormStatusGraph.State.STARTED, NormStatusGraph.State.STOPPED),
            StatusValue(self.__stop)
        )
        graph_tmp.add(
            StatusEdge(NormStatusGraph.State.STOPPED, NormStatusGraph.State.EXITED),
            StatusValue(self.__exit)
        )
        graph_tmp.build(0)
        return graph_tmp

    async def __start(self):
        self.status2target(self.__class__.State.STARTED)

    async def __stop(self):
        self.status2target(self.__class__.State.STOPPED)

    async def __exit(self):
        self.status2target(self.__class__.State.EXITED)

    async def _starting(self):
        """
        启动中状态运行函数(子类需要重写这个函数)
        """
        raise Exception('子类需要重写这个函数')
    pass


class SignFlowBase:
    """信号处理loop
    1. 有信号时处理状态转换
    2. 无信号时处理状态运行时
    """
    def __init__(self, graph: StatusGraphBase) -> None:
        self._graph = graph
        self._exit_status = None
        self.__callable_order = CallableOrder(self.__sign_deal)
        self.__lock = asyncio.Lock()
        self._running = False
        pass

    async def __sign_deal(self, status_target, *args, **kwds):
        # 信号处理函数，所有状态转换理论上都应该在这里
        func = self._graph.func_get_target(status_target)
        if func is None:
            return None
        res = func(*args, **kwds)
        return await res if asyncio.iscoroutinefunction(func) else res

    async def __no_sign(self):
        func = self._graph.func_get()
        if func is None:
            return await self.__callable_order.queue_wait()
        res_pre = func()
        return await res_pre if asyncio.iscoroutinefunction(func) else res_pre

    async def _main(self):
        self.__running_err()
        async with self.__lock:
            self._running = True
            while self._exit_status is None or self._graph._status != self._exit_status:
                while not await self.__callable_order.queue_no_wait():
                    await self.__no_sign()
                pass
            self._running = False
            pass
        pass

    def __running_err(self):
        if self._running:
            raise Exception('已有loop在运行中')

    async def _call(self, *args, **kwds):
        return await self.__callable_order.call(*args, **kwds)
    pass


class NormSignFlow(SignFlowBase):
    """普通的信号流-开放端口给管理员
    1. 开放启动流端口给管理员
    2. 开放状态流转端口给管理员
    """
    def __init__(self, graph: NormStatusGraph) -> None:
        super().__init__(graph)
        self._exit_status = NormStatusGraph.State.EXITED
        pass

    async def launch(self):
        # 启动状态流，并将状态转移至started
        if self._running or self._graph._status != self._exit_status:
            raise Exception(f'状态机启动失败|status:{self._graph._status}|run:{self._running}')
        self._graph.status2target(NormStatusGraph.State.STARTED)
        return await self._main()

    async def start(self):
        # 将状态转移至started
        if not self._running:
            raise Exception('状态机尚未启动')
        return await self._call(NormStatusGraph.State.STARTED)

    async def stop(self):
        # 将状态转移至stopped
        if not self._running:
            raise Exception('状态机尚未启动')
        return await self._call(NormStatusGraph.State.STOPPED)

    async def exit(self):
        # 将状态转移至exited
        if not self._running:
            raise Exception('状态机尚未启动')
        return await self._call(NormStatusGraph.State.EXITED)
    pass


# class NormFlow(NormSignFlow, NormStatusGraph):
#     def __init__(self) -> None:
#         NormSignFlow.__init__(self, self)
#         NormStatusGraph.__init__(self)
#         pass
#     pass


# class QueueOwnerFlow(NormFlow):
#     def __init__(self, q: NormManageQueue, match_case: MatchCase) -> None:
#         self.__q = q
#         self.__match_case = match_case
#         super().__init__()
#         pass

#     @property
#     def queue(self):
#         return self.__q.q_action

#     async def _stop_async(self):
#         task = AsyncBase.coro2task_exec(self._sign_change(NormStatusGraph.State.STOPPED))
#         await self.__q.q_step.step()
#         future_res = await task
#         return future_res > 0

#     async def _starting(self):
#         state, args, kwds = await self.__q.q_step.get()
#         await self.__match_case.match(state, *args, **kwds)
#         self.__q.q_step.task_done()
#         pass
#     pass
