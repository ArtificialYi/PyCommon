import asyncio
from asyncio import Task
from typing import Dict
from .status import StatusValue, StatusGragh, StatusEdge
from enum import Enum, auto
from ..tool.base import AsyncBase, MatchCase
from .queue import NormManageQueue


class GraphBase:
    def __init__(self) -> None:
        self.__doing_dict = {}
        self._status = None
        self.__status_graph: StatusGragh = self._graph_build()
        pass

    def status_doing(self):
        return self.__doing_dict.get(self._status, None)

    def status_change(self, status):
        value = self.__status_graph.get(self._status, status)
        return None if value is None or value.coro is None else value.coro

    def status2target(self, status):
        self._status = status
        pass

    def _graph_build(self):  # pragma : no cover
        """
        状态转移方程式
        需要子类重写
        """
        raise Exception('子类需要重写这个函数')

    def _doing_dict_init(self, doing_dict: Dict):
        self.__doing_dict = doing_dict
        pass
    pass


class SignResultFlow:
    """
    结果型信号(状态直达)
    1. 处理每个信号
    """
    def __init__(self, graph: GraphBase) -> None:
        self.__q_sign = asyncio.Queue()
        self.__graph = graph
        self._exit_status = None
        pass

    @property
    def _graph(self):
        return self.__graph

    def __call__(self) -> Task:
        return AsyncBase.coro2task_exec(self._sign())

    async def _sign(self):
        """同一个对象同时执行一个信号接收器
        信号处理程序：处理每个信号
        1. 是否存在新命令，是2，否5
        2. 获取一条命令（等待型）
        3. 执行一条命令
        4. 直至当前命令完成，返回完成
        5. 是否存在状态时，存在则执行一次，然后1，不存在则2
        """
        status = None
        while self._exit_status is None or status != self._exit_status:
            while (self.__q_sign.qsize() == 0) and ((coro := self.__graph.status_doing()) is not None):
                await coro()

            # 执行一个命令
            status, future, args, kwargs = await self.__q_sign.get()
            res_action = await self.__action(status, *args, **kwargs)
            # 回调：可实现sign的wait
            future.set_result(res_action)
            self.__q_sign.task_done()
            pass
        pass

    async def __action(self, status, *args, **kwargs):
        coro = self.__graph.status_change(status)
        time_res = 0
        while coro is not None:
            await coro(*args, **kwargs)
            coro = self.__graph.status_change(status)
            time_res += 1
            pass
        return time_res

    async def _sign_put_no_pause(self, status, *args, **kwargs):
        future = AsyncBase.get_future()
        await self.__q_sign.put((status, future, args, kwargs))
        return await future

    async def _sign_put_pause(self, status, *args, **kwargs):
        future = AsyncBase.get_future()
        await self.__q_sign.put((status, future, args, kwargs))
        return future
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
        self._doing_dict_init({
            NormMachineGraph.State.STARTED: self._starting,
        })
        self.status2target(NormMachineGraph.State.EXITED)
        pass

    def _graph_build(self):
        graph_tmp = StatusGragh()
        graph_tmp.add(
            StatusEdge(NormMachineGraph.State.STOPPED, NormMachineGraph.State.STARTED),
            StatusValue(1, self.__start)
        )
        graph_tmp.add(
            StatusEdge(NormMachineGraph.State.STARTED, NormMachineGraph.State.STOPPED),
            StatusValue(1, self.__stop)
        )
        graph_tmp.add(
            StatusEdge(NormMachineGraph.State.STOPPED, NormMachineGraph.State.EXITED),
            StatusValue(1, self.__exit)
        )
        graph_tmp.build(0)
        return graph_tmp

    async def __start(self, *args, **kwds):
        self.status2target(self.__class__.State.STARTED)

    async def __stop(self, *args, **kwds):
        self.status2target(self.__class__.State.STOPPED)

    async def __exit(self, *args, **kwds):
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
        future = await self._sign_put_pause(NormMachineGraph.State.STOPPED)
        await self.__q.q_step.step()
        future_res = await future
        return future_res > 0

    async def _starting(self):
        state, args, kwds = await self.__q.q_step.get()
        await self.__match_case.match(state, *args, **kwds)
        self.__q.q_step.task_done()
        pass
    pass
