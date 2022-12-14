import asyncio

from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout
from ...src.tool.base import AsyncBase
from ...src.machine.status import NormStatusGraph
from ...src.machine.mode import NormStatusSignFlow, StatusSignFlowBase


class FuncTmp:
    def __init__(self) -> None:
        self.num = 0
        pass

    async def func(self):
        self.num += 1
        return await asyncio.sleep(0.1)
    pass


class TestSignFlowBase:
    @PytestAsyncTimeout(3)
    async def test(self):
        func_tmp = FuncTmp()
        graph = NormStatusGraph(func_tmp.func)
        sign_flow = StatusSignFlowBase(graph)
        # 未启动
        assert not sign_flow._future_run.done()
        # 启动，无信号，_starting被调用
        assert func_tmp.num == 0
        task_main = AsyncBase.coro2task_exec(sign_flow._main())
        await sign_flow._future_run
        await asyncio.sleep(1)
        assert func_tmp.num > 0
        assert not task_main.done()

        # 启动中，再次启动会抛出启动中异常
        assert await FuncTool.is_func_err(sign_flow._main)

        # 信号处理，状态变更-成功
        assert sign_flow._graph.status == NormStatusGraph.State.STARTED
        assert await sign_flow._sign_deal(NormStatusGraph.State.STOPPED)
        assert sign_flow._graph.status == NormStatusGraph.State.STOPPED

        # 启动中，无信号，无运行时，死锁
        num = func_tmp.num
        await asyncio.sleep(1)
        assert func_tmp.num == num

        # 信号处理，关闭主流程
        assert sign_flow._graph.status == NormStatusGraph.State.STOPPED
        assert await sign_flow._sign_deal(NormStatusGraph.State.EXITED)
        assert sign_flow._graph.status == NormStatusGraph.State.EXITED
        await task_main
        assert not sign_flow._future_run.done()
        pass
    pass


class TestNormStatusGraph:
    @PytestAsyncTimeout(2)
    async def test(self):
        func_tmp = FuncTmp()
        norm_sign_flow = NormStatusSignFlow(func_tmp.func)

        # 启动，无信号，_starting被调用
        assert func_tmp.num == 0
        graph = norm_sign_flow._graph
        assert graph.status == NormStatusGraph.State.STARTED
        task_main = AsyncBase.coro2task_exec(norm_sign_flow.launch())
        await norm_sign_flow._future_run
        await asyncio.sleep(1)
        assert norm_sign_flow._future_run.done()
        assert func_tmp.num > 0
        assert not task_main.done()

        # 启动中无法再次启动
        assert await FuncTool.is_func_err(norm_sign_flow.launch)

        # 状态转移-started->stopped
        assert await norm_sign_flow.stop()
        assert graph.status == NormStatusGraph.State.STOPPED

        # 状态转移-stopped->started
        assert await norm_sign_flow.start()
        assert graph.status == NormStatusGraph.State.STARTED

        # 状态转移-started->exited
        assert await norm_sign_flow.exit()
        await task_main
        assert graph.status == NormStatusGraph.State.EXITED

        # 状态错误无法启动
        assert await FuncTool.is_func_err(norm_sign_flow.launch)

        # 未启动，无法发送状态转移信号
        assert await FuncTool.is_func_err(norm_sign_flow.start)
        assert await FuncTool.is_func_err(norm_sign_flow.stop)
        assert await FuncTool.is_func_err(norm_sign_flow.exit)
        pass
    pass


class TestNormFlowManage:
    def test(self):
        pass
    pass
