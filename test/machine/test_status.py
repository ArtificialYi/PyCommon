
from ...src.machine.status import StatusEdge, StatusGraph, StatusValue


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
    def test_error(self):
        try:
            StatusGraph().add(StatusEdge(0, 0), StatusValue(None, None))
        except Exception:
            assert True
            pass
        else:
            assert False
        pass

    def test_init(self):
        """
        2点1边无回路
        """
        a = StatusGraph()
        a.add(StatusEdge(0, 1), StatusValue(1, 3))
        # 无效插入
        a.add(StatusEdge(0, 1), StatusValue(2, float('inf')))
        # 一条基本边
        assert a.num_edge == 1
        a.build()
        assert a.status_gragh[0][1].weight == 1
        assert a.status_gragh[1][0].weight == float('inf')
        pass

    def test_edge2(self):
        """
        3点2边无回路
        """
        a = StatusGraph()
        a.add(StatusEdge(0, 1), StatusValue(1, 3))
        a.add(StatusEdge(1, 2), StatusValue(2, 4))
        # 两条基本边
        assert a.num_edge == 2
        a.build()
        # 基本数值
        assert a.status_gragh[0][1].weight == 1
        assert a.status_gragh[1][2].weight == 2
        assert a.status_gragh[0][2].weight == 1 + 2
        # 无效边
        assert a.status_gragh[1][0].weight == float('inf')
        assert a.status_gragh[2][0].weight == float('inf')
        assert a.status_gragh[2][1].weight == float('inf')
        # 只有单边
        a.build(0)
        assert a.status_gragh[0][2].weight == float('inf')
        pass

    def test_edge4(self):
        """
        4点4边无回路
        """
        a = StatusGraph()
        a.add(StatusEdge(0, 1), StatusValue(1, 3))
        a.add(StatusEdge(1, 2), StatusValue(2, 4))
        a.add(StatusEdge(1, 3), StatusValue(4, 5))
        a.add(StatusEdge(2, 3), StatusValue(1, 6))
        # 四条边
        assert a.num_edge == 4
        a.build()
        # 双边
        assert a.status_gragh[0][2].weight == 1 + 2
        # 3边
        assert a.status_gragh[0][3].weight == 1 + 2 + 1
        # 双边覆盖单边
        assert a.status_gragh[1][3].weight == 2 + 1

        a.build(0)
        # 只有单边
        assert a.status_gragh[0][2].weight == float('inf')
        assert a.status_gragh[0][3].weight == float('inf')
        assert a.status_gragh[1][3].weight == 4

        a.build(1)
        # 允许双边,但3边依旧不行
        assert a.status_gragh[0][3].weight == 1 + 4
        pass

    def test_edge_self(self):
        """
        4点5边有回路
        自身无法链路到自身
        """
        # 自身无法链路到自身
        a = StatusGraph()
        a.add(StatusEdge(1, 3), StatusValue(4, 5))
        a.add(StatusEdge(0, 1), StatusValue(1, 3))
        a.add(StatusEdge(1, 2), StatusValue(2, 4))
        a.add(StatusEdge(2, 3), StatusValue(1, 6))
        a.add(StatusEdge(3, 0), StatusValue(5, 7))
        a.build()
        b = a.get(0, 3)
        assert b is not None
        assert b.coro == 3
        assert b.weight == 1 + 3
        assert b.count == 2
        for i in range(4):
            assert a.status_gragh[i].get(i, None) is None
            pass
        pass
    pass
