import asyncio

from ..tool.base import AsyncBase
from .status import NormStatusGraph
from ..tool.func_tool import Func2CallableOrderSync


class StatusSignFlowBase(Func2CallableOrderSync):
    """信号处理loop-生命周期与loop一致
    1. 有信号时处理状态转换
    2. 无信号时处理状态运行时
    """
    def __init__(self, graph: NormStatusGraph) -> None:
        self._graph = graph
        self._future_run = AsyncBase.get_future()
        self.__lock = asyncio.Lock()
        # 封装和替换
        Func2CallableOrderSync.__init__(self, self._sign_deal)
        self.__handle_sign = Func2CallableOrderSync.__call__(self)
        pass

    async def _sign_deal(self, status_target, *args, **kwds):
        # 函数内部统一使用self.__handle_sign来调用
        func = self._graph.func_get_target(status_target)
        if func is None:
            return None
        res = func(*args, **kwds)
        return await res if asyncio.iscoroutinefunction(func) else res

    async def __no_sign(self):
        func = self._graph.func_get()
        if func is None:
            return await self.__handle_sign.queue_wait()
        res_pre = func()
        return await res_pre if asyncio.iscoroutinefunction(func) else res_pre

    async def _main(self):
        self.__running_err()
        async with self.__lock:
            self._future_run.set_result(True)
            while self._graph._status != self._graph._exited_status:
                if await self.__handle_sign.queue_no_wait():
                    continue
                await self.__no_sign()
                pass
            self._future_run = AsyncBase.get_future()
            pass
        pass

    def __running_err(self):
        if self._future_run.done():
            raise Exception('已有loop在运行中')
    pass


class NormStatusSignFlow(StatusSignFlowBase):
    """普通的信号流-开放端口给管理员
    1. 开放启动流端口给管理员
    2. 开放状态流转端口给管理员
    """
    def __init__(self, graph: NormStatusGraph) -> None:
        super().__init__(graph)
        pass

    async def launch(self):
        # 启动状态流，并将状态转移至started
        if self._future_run.done() or self._graph._status != self._graph._exited_status:
            raise Exception(f'状态机启动失败|status:{self._graph._status}|run:{self._future_run.done()}')
        self._graph.status2target(NormStatusGraph.State.STARTED)
        return await self._main()

    async def start(self):
        # 将状态转移至started
        if not self._future_run.done():
            raise Exception('状态机尚未启动')
        return await self._sign_deal(NormStatusGraph.State.STARTED)

    async def stop(self):
        # 将状态转移至stopped
        if not self._future_run.done():
            raise Exception('状态机尚未启动')
        return await self._sign_deal(NormStatusGraph.State.STOPPED)

    async def exit(self):
        # 将状态转移至exited
        if not self._future_run.done():
            raise Exception('状态机尚未启动')
        return await self._sign_deal(NormStatusGraph.State.EXITED)
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
