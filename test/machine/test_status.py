from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout
from ...src.machine.status import SGForFlow, SGMachineForFlow, StatusEdge, StatusGraph, StatusValue


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
        assert (value := a.get(0, 1)) is not None and value.weight == 1
        assert (value := a.get(1, 0)) is not None and value.weight == float('inf')
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
        assert (value := a.get(0, 1)) is not None and value.weight == 1
        assert (value := a.get(1, 2)) is not None and value.weight == 2
        assert (value := a.get(0, 2)) is not None and value.weight == 1 + 2
        # 无效边
        assert (value := a.get(1, 0)) is not None and value.weight == float('inf')
        assert (value := a.get(2, 0)) is not None and value.weight == float('inf')
        assert (value := a.get(2, 1)) is not None and value.weight == float('inf')
        # 只有单边
        a.build(0)
        assert (value := a.get(0, 2)) is not None and value.weight == float('inf')
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
        assert (value := a.get(0, 2)) is not None and value.weight == 1 + 2
        # 3边
        assert (value := a.get(0, 3)) is not None and value.weight == 1 + 2 + 1
        # 双边覆盖单边
        assert (value := a.get(1, 3)) is not None and value.weight == 2 + 1

        a.build(0)
        # 只有单边
        assert (value := a.get(0, 2)) is not None and value.weight == float('inf')
        assert (value := a.get(0, 3)) is not None and value.weight == float('inf')
        assert (value := a.get(1, 3)) is not None and value.weight == 4

        a.build(1)
        # 允许双边,但3边依旧不行
        assert (value := a.get(0, 3)) is not None and value.weight == 1 + 4
        pass

    def test_edge_self(self):
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
            assert a.get(i, i) is None
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
        assert (value := a.get(0, 0)) is not None and value.weight == float('inf')
        pass
    pass


class TestSGFlowMachine:
    """基本状态图
    """
    @PytestAsyncTimeout(1)
    async def test(self):
        graph = SGMachineForFlow(SGForFlow(FuncTool.norm_sync_err))
        assert graph.status == SGForFlow.State.EXITED
        assert graph.func_get() is None

        # 状态无法转移
        assert await graph.status_change(SGForFlow.State.EXITED) is None
        # 状态转移成功
        assert await graph.status_change(SGForFlow.State.STARTED)
        # started状态内函数调用成功
        assert await FuncTool.is_async_err(graph.status_change, SGForFlow.State.STARTED)
        pass
    pass
