import asyncio
import pytest
from ...src.tool.base import AsyncBase
from ...src.machine.status import FuncQueue, StatusEdge, StatusGraph, StatusValue


class TestFuncQueue(object):
    @pytest.mark.timeout(4)
    @pytest.mark.asyncio
    async def test_queue_empty(self):
        """空队列的函数测试
        """
        # 全默认
        assert await FuncQueue().inner() is None
        func0 = FuncQueue()
        task0 = AsyncBase.coro2task_exec(func0.func())
        await asyncio.sleep(1)
        assert not task0.done()
        res_call0 = await func0.inner()
        assert res_call0 is None
        assert await task0 is None
        # default何时被调用
        assert await FuncQueue(lambda: 0).inner() == 0

        # inner是在call的时候才会被调用
        func1 = FuncQueue(lambda: 0, lambda: 1)
        task1 = AsyncBase.coro2task_exec(func1.func())
        await asyncio.sleep(1)
        assert not task1.done()
        res_call1 = await func1.inner()
        assert res_call1 == 1 == await task1

        # 默认情况也不走default
        func2 = FuncQueue(lambda: 0, lambda: 1, lambda: False,)
        task2 = AsyncBase.coro2task_exec(func2.inner())
        await asyncio.sleep(1)
        assert not task2.done()
        res_func0 = await func2.func()
        assert res_func0 == await task2 == 1
    pass


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


class TestStatusGragh(object):
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
        a.add(StatusEdge(1, 3), StatusValue(FuncQueue(lambda: 5), 4))
        a.add(StatusEdge(0, 1), StatusValue(FuncQueue(lambda: 3), 1))
        a.add(StatusEdge(1, 2), StatusValue(FuncQueue(lambda: 4), 2))
        a.add(StatusEdge(2, 3), StatusValue(FuncQueue(lambda: 6), 1))
        a.add(StatusEdge(3, 0), StatusValue(FuncQueue(lambda: 7), 5))
        a.build()
        b = a.get(0, 3)
        assert b is not None and b.func_queue is not None
        assert await b.func_queue.inner() == 3
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
