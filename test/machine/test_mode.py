import asyncio
import pytest

from ...src.tool.func_tool import FuncTool
from ...src.tool.base import AsyncBase
from ...src.machine.status import NormStatusGraph
from ...src.machine.mode import SignFlowBase


class GraphTmp(NormStatusGraph):
    num = 0

    async def _starting(self):
        GraphTmp.num += 1
        return await asyncio.sleep(0.1)
    pass


class TestSignFlowBase:
    async def func(self):
        return await asyncio.sleep(1)

    @pytest.mark.timeout(4)
    @pytest.mark.asyncio
    async def test(self):
        sign_flow = SignFlowBase(GraphTmp())
        # 未启动
        assert not sign_flow._running
        # 启动，无信号，_starting被调用
        assert GraphTmp.num == 0
        sign_flow._graph.status2target(NormStatusGraph.State.STARTED)
        task_main = AsyncBase.coro2task_exec(sign_flow._main())
        await asyncio.sleep(1)
        assert sign_flow._running
        assert GraphTmp.num > 0
        assert not task_main.done()

        # 启动中，再次启动会抛出启动中异常
        assert await FuncTool.func_err(sign_flow._main)

        # 信号处理，状态变更-失败
        assert sign_flow._graph._status == NormStatusGraph.State.STARTED
        assert await sign_flow._call(NormStatusGraph.State.EXITED) is None
        assert sign_flow._graph._status == NormStatusGraph.State.STARTED

        # 信号处理，状态变更-成功
        assert sign_flow._graph._status == NormStatusGraph.State.STARTED
        assert await sign_flow._call(NormStatusGraph.State.STOPPED)
        assert sign_flow._graph._status == NormStatusGraph.State.STOPPED

        # 无信号，无运行时，死锁
        num = GraphTmp.num
        await asyncio.sleep(1)
        assert GraphTmp.num == num

        # 信号处理，关闭主流程
        assert sign_flow._graph._status == NormStatusGraph.State.STOPPED
        assert await sign_flow._call(NormStatusGraph.State.EXITED)
        await task_main
        assert sign_flow._graph._status == NormStatusGraph.State.EXITED
        assert not sign_flow._running
        pass
    pass
