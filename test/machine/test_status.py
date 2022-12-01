import asyncio
import pytest
from ...src.tool.func_tool import FuncTool
from ...src.machine.status import NormStatusGraph, StatusEdge, StatusGraph, StatusValue


class TestStatusEdge(object):
    def test_init(self):
        a = [
            StatusEdge(0, 1),
            StatusEdge(0, 1),
            StatusEdge(0, 2)
        ]
        assert a[0] == a[1]
        assert a[1] != a[2]

        b = set()
        [b.add(unit) for unit in a]
        assert len(b) == 2
        pass
    pass


class TestStatusGraph(object):
    # def test_error(self):
    #     """已舍弃，可以连接自身了
    #     """
    #     try:
    #         StatusGraph().add(StatusEdge(0, 0), StatusValue(None))
    #     except Exception:
    #         assert True
    #         pass
    #     else:
    #         assert False
    #     pass

    def test_init(self):
        """
        2点1边无回路
        """
        a = StatusGraph()
        a.add(StatusEdge(0, 1), StatusValue(None, 1))
        # 无效插入
        a.add(StatusEdge(0, 1), StatusValue(None, 2))
        # 一条基本边
        assert a.num_edge == 1
        a.build()
        assert a.status_graph[0][1].weight == 1
        assert a.status_graph[1][0].weight == float('inf')
        pass

    def test_edge2(self):
        """
        3点2边无回路
        """
        a = StatusGraph()
        a.add(StatusEdge(0, 1), StatusValue(None, 1))
        a.add(StatusEdge(1, 2), StatusValue(None, 2))
        # 两条基本边
        assert a.num_edge == 2
        a.build()
        # 基本数值
        assert a.status_graph[0][1].weight == 1
        assert a.status_graph[1][2].weight == 2
        assert a.status_graph[0][2].weight == 1 + 2
        # 无效边
        assert a.status_graph[1][0].weight == float('inf')
        assert a.status_graph[2][0].weight == float('inf')
        assert a.status_graph[2][1].weight == float('inf')
        # 只有单边
        a.build(0)
        assert a.status_graph[0][2].weight == float('inf')
        pass

    def test_edge4(self):
        """
        4点4边无回路
        """
        a = StatusGraph()
        a.add(StatusEdge(0, 1), StatusValue(None, 1))
        a.add(StatusEdge(1, 2), StatusValue(None, 2))
        a.add(StatusEdge(1, 3), StatusValue(None, 4))
        a.add(StatusEdge(2, 3), StatusValue(None, 1))
        # 四条边
        assert a.num_edge == 4
        a.build()
        # 双边
        assert a.status_graph[0][2].weight == 1 + 2
        # 3边
        assert a.status_graph[0][3].weight == 1 + 2 + 1
        # 双边覆盖单边
        assert a.status_graph[1][3].weight == 2 + 1

        a.build(0)
        # 只有单边
        assert a.status_graph[0][2].weight == float('inf')
        assert a.status_graph[0][3].weight == float('inf')
        assert a.status_graph[1][3].weight == 4

        a.build(1)
        # 允许双边,但3边依旧不行
        assert a.status_graph[0][3].weight == 1 + 4
        pass

    @pytest.mark.timeout(1)
    @pytest.mark.asyncio
    async def test_edge_self(self):
        """
        4点5边有回路
        自身无法链路到自身
        """
        # 自身无法链路到自身
        a = StatusGraph()
        a.add(StatusEdge(1, 3), StatusValue(lambda: 5, 4))
        a.add(StatusEdge(0, 1), StatusValue(lambda: 3, 1))
        a.add(StatusEdge(1, 2), StatusValue(lambda: 4, 2))
        a.add(StatusEdge(2, 3), StatusValue(lambda: 6, 1))
        a.add(StatusEdge(3, 0), StatusValue(lambda: 7, 5))
        a.build()
        b = a.get(0, 3)
        assert b is not None and b.func is not None
        assert b.func() == 3
        assert b.weight == 1 + 3
        assert b.count == 2
        for i in range(4):
            assert a.status_graph[i].get(i, None) is None
            pass
        pass

    def test_self(self):
        """
        自身可以连接自身（仅作为特殊边，不加入计算）
        """
        a = StatusGraph()
        a.add(StatusEdge(0, 0), StatusValue(None))
        a.build()
        assert a.num_edge == 1
        assert a.status_graph[0].get(0, None) is not None
        pass
    pass


class TestNormStatusGraph:
    @pytest.mark.timeout(1)
    @pytest.mark.asyncio
    async def test(self):
        graph = NormStatusGraph()
        assert graph._status == NormStatusGraph.State.EXITED
        graph.status2target(NormStatusGraph.State.STARTED)
        assert graph._status == NormStatusGraph.State.STARTED
        # STARTED状态刚好有函数，但是是会抛出异常的
        func0 = graph.func_get()
        assert func0 is not None and asyncio.iscoroutinefunction(func0)
        assert await FuncTool.func_err(func0)

        # STOPPED状态下没有运行时函数
        graph.status2target(NormStatusGraph.State.STOPPED)
        assert graph._status == NormStatusGraph.State.STOPPED
        assert graph.func_get() is None

        # 转换函数-stopped->started运行成功
        func1 = graph.func_get_target(NormStatusGraph.State.STARTED)
        assert func1 is not None and asyncio.iscoroutinefunction(func1)
        assert graph._status == NormStatusGraph.State.STOPPED
        await func1()
        assert graph._status == NormStatusGraph.State.STARTED

        # 转换函数-started->started运行成功
        func2 = graph.func_get_target(NormStatusGraph.State.STARTED)
        assert func2 is not None and asyncio.iscoroutinefunction(func2)
        assert graph._status == NormStatusGraph.State.STARTED
        assert await FuncTool.func_err(func2)
        assert graph._status == NormStatusGraph.State.STARTED

        # 转换函数-started->exited失败
        func3 = graph.func_get_target(NormStatusGraph.State.EXITED)
        assert func3 is None

        # 转换函数-started->stopped成功
        func4 = graph.func_get_target(NormStatusGraph.State.STOPPED)
        assert func4 is not None and asyncio.iscoroutinefunction(func4)
        assert graph._status == NormStatusGraph.State.STARTED
        await func4()
        assert graph._status == NormStatusGraph.State.STOPPED

        # 转换函数-stopped->exited成功
        func5 = graph.func_get_target(NormStatusGraph.State.EXITED)
        assert func5 is not None and asyncio.iscoroutinefunction(func5)
        assert graph._status == NormStatusGraph.State.STOPPED
        await func5()
        assert graph._status == NormStatusGraph.State.EXITED
        pass
    pass
