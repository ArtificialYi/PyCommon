import asyncio
from asyncio import Task
from typing import Union
from .status import CallableOrder, FuncQueue, StatusValue, StatusGraph, StatusEdge
from enum import Enum, auto
from ..tool.base import AsyncBase, MatchCase
from .queue import NormManageQueue


class GraphBase:
    def __init__(self) -> None:
        self._status = None
        self.__status_graph: StatusGraph = self._graph_build()
        pass

    def status2target(self, status):
        self._status = status
        pass

    def _graph_build(self):  # pragma : no cover
        """
        状态转移方程式
        需要子类重写
        """
        raise Exception('子类需要重写这个函数')

    def exist_func(self):
        return self.__status_graph.get(self._status, self._status) is not None

    def func_get(self) -> Union[FuncQueue, None]:
        value = self.__status_graph.get(self._status, self._status)
        return value.func_queue if value is not None else None

    def func_get_target(self, status):
        value = self.__status_graph. get(self._status, status)
        return value.func_queue if value is not None else None
    pass


class SignResultFlow:
    """信号处理loop
    1. 有信号时处理机制，无信号时处理机制
    """
    def __init__(self, graph: GraphBase) -> None:
        self.__graph = graph
        self._exit_status = None
        self.__callable_order = CallableOrder(self.__sign_deal)
        pass

    async def __sign_deal(self, status_target, *args, **kwds):
        func = self.__graph.func_get_target(status_target)
        res = func(*args, **kwds) if func is not None else None
        return await res if asyncio.iscoroutinefunction(func) else res

    async def __no_sign(self):
        func = self.__graph.func_get()
        if func is None:
            await self.__callable_order.queue_wait()
        res_pre = func()
        await res_pre if asyncio.iscoroutinefunction(func) else res_pre

    async def _sign(self):
        status = None
        while self._exit_status is None or status != self._exit_status:
            while not await self.__callable_order.queue_no_wait():
                await self.__no_sign()
            pass
        pass

    def __call__(self) -> Task:
        """异步调用
        """
        return AsyncBase.coro2task_exec(self._sign())
    pass


class NormMachineGraph(GraphBase):
    """最基本的状态机
    """
    class State(Enum):
        STARTED = auto()
        STOPPED = auto()
        EXITED = auto()
        pass

    def __init__(self) -> None:
        GraphBase.__init__(self)
        self.status2target(NormMachineGraph.State.EXITED)
        pass

    def _graph_build(self):
        graph_tmp = StatusGraph()
        graph_tmp.add(
            StatusEdge(NormMachineGraph.State.STOPPED, NormMachineGraph.State.STARTED),
            StatusValue(FuncQueue(self.__start))
        )
        graph_tmp.add(
            StatusEdge(NormMachineGraph.State.STARTED, NormMachineGraph.State.STOPPED),
            StatusValue(FuncQueue(self.__stop))
        )
        graph_tmp.add(
            StatusEdge(NormMachineGraph.State.STOPPED, NormMachineGraph.State.EXITED),
            StatusValue(FuncQueue(self.__exit))
        )
        graph_tmp.build(0)
        return graph_tmp

    async def __start(self):
        self.status2target(self.__class__.State.STARTED)

    async def __stop(self):
        self.status2target(self.__class__.State.STOPPED)

    async def __exit(self):
        self.status2target(self.__class__.State.EXITED)

    async def _starting(self):  # pragma : no cover
        """
        启动中状态运行函数(子类需要重写这个函数)
        """
        raise Exception('子类需要重写这个函数')
    pass


class NormMachineAction(SignResultFlow):
    """对象唯一性
    """
    def __init__(self, graph: NormMachineGraph) -> None:
        super().__init__(graph)
        self.__task = None
        self.__lock_action = asyncio.Lock()
        self._exit_status = NormMachineGraph.State.EXITED
        pass

    def __call__(self):
        # 该函数同一时间应该只会运行一个，直到task已完成
        if self.__task is not None and not self.__task.done():
            return self.__task

        if self._graph._status != self._exit_status:  # pragma : no cover
            raise Exception(f'状态异常,状态机启动失败:{self._graph._status}')
        self._graph.status2target(NormMachineGraph.State.STARTED)
        self.__task = super().__call__()
        return self.__task

    async def start(self, *args, **kwds):
        if self.__task is None or self.__task.done():
            return False

        async with self.__lock_action:
            if self.__task is None or self.__task.done():
                return False
            res_start = await self._start_async(*args, **kwds)
            pass
        return res_start

    async def _start_async(self, *args, **kwargs):
        return (await self._sign_put_no_pause(NormMachineGraph.State.STARTED, *args, **kwargs)) > 0

    async def stop(self, *args, **kwds):
        if self.__task is None or self.__task.done():
            return False

        async with self.__lock_action:
            if self.__task is None or self.__task.done():
                return False
            res_stop = await self._stop_async(*args, **kwds)
            pass
        return res_stop

    async def _stop_async(self, *args, **kwargs):
        return (await self._sign_put_no_pause(NormMachineGraph.State.STOPPED, *args, **kwargs)) > 0

    async def exit(self, *args, **kwargs):
        """退出流
        1. 发送停止信号
        2. 确认流已经停止
        """
        if self.__task is None or self.__task.done():
            return False

        async with self.__lock_action:
            exit_res = await self.__exit_async(self._exit_status, *args, **kwargs)
            pass
        return exit_res

    async def __exit_async(self, *args, **kwargs):
        if self.__task is None or self.__task.done():
            return False

        future_res = await self._sign_put_no_pause(self._exit_status, *args, **kwargs)
        await self.__task
        return future_res > 0
    pass


class NormFlow(NormMachineAction, NormMachineGraph):
    def __init__(self) -> None:
        NormMachineAction.__init__(self, self)
        NormMachineGraph.__init__(self)
        pass
    pass


class QueueOwnerFlow(NormFlow):
    def __init__(self, q: NormManageQueue, match_case: MatchCase) -> None:
        self.__q = q
        self.__match_case = match_case
        super().__init__()
        pass

    @property
    def queue(self):
        return self.__q.q_action

    async def _stop_async(self):
        task = AsyncBase.coro2task_exec(self._sign_change(NormMachineGraph.State.STOPPED))
        await self.__q.q_step.step()
        future_res = await task
        return future_res > 0

    async def _starting(self):
        state, args, kwds = await self.__q.q_step.get()
        await self.__match_case.match(state, *args, **kwds)
        self.__q.q_step.task_done()
        pass
    pass
