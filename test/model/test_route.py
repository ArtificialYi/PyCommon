from ...src.model.route import AlLossUnit, ArgsLatitude, RouteDict, RouteHeap, RouteUnit


class TestRoute:
    def test_init(self):
        # 初始化route
        route_unit = RouteUnit(RouteHeap(RouteDict()), RouteHeap(RouteDict()))
        assert route_unit.pop() is not None
        assert route_unit.pop() is None
        pass

    def test_add_fail_norm(self):
        # 无法刷新loss差不多的节点
        route_unit = RouteUnit(RouteHeap(RouteDict()), RouteHeap(RouteDict()))
        node_tmp = route_unit.pop()
        assert node_tmp is not None
        assert not route_unit.push(node_tmp.al, node_tmp.loss_pre)
        pass

    def test_add_last(self):
        route_unit = RouteUnit(RouteHeap(RouteDict()), RouteHeap(RouteDict()))
        node_tmp = route_unit.pop()
        assert node_tmp is not None
        assert route_unit.push(node_tmp.al, 1)
        # 刷新最后一个节点后，next节点为空
        assert route_unit.pop() is None
        pass

    def test_add_norm(self):
        route_unit = RouteUnit(RouteHeap(RouteDict(length_max=2, layer_max=4)), RouteHeap(RouteDict()))
        node_tmp = route_unit.pop()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 2)

        # 刷新1，1，2节点，下一个节点为2，1，2
        assert route_unit.push(node_tmp.al, 1)
        node_tmp = route_unit.pop()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(2, 1, 2)

        # 刷新2，1，2节点，下一个节点为1，1，4（新节点不一定保留单测）
        assert route_unit.push(node_tmp.al, 0.3)
        node_tmp = route_unit.pop()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 4)

        # 刷新1，1，4节点，下一个节点为1，1, 8
        assert route_unit.push(node_tmp.al, 0.9)
        node_tmp = route_unit.pop()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 8)

        # 插入1，1，8节点失败，下一个节点为1，2，4
        assert route_unit.push(node_tmp.al, 0.85)
        node_tmp = route_unit.pop()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 2, 4)

        # 刷新1，2，4节点，下一个节点为1，1, 16(1，1，16的前置是1，1，8)
        assert route_unit.push(node_tmp.al, 0.8)
        node_tmp = route_unit.pop()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 16) and node_tmp.loss_pre == 0.85
        pass

    def test_add_pre(self):
        heap_pre = RouteHeap(RouteDict())
        node_tmp = heap_pre.pop()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 2)
        assert heap_pre.push(node_tmp.al, 1)
        assert heap_pre.pop() is None

        route_unit = RouteUnit(RouteHeap(RouteDict()), heap_pre)
        assert route_unit.pop() is None
        pass

    def test_al(self):
        a = AlLossUnit(ArgsLatitude(1, 1, 2), 1)
        b = AlLossUnit(ArgsLatitude(1, 1, 2), 2)
        assert a > b

        c = AlLossUnit(ArgsLatitude(1, 1, 2), 1)
        assert a == c
    pass
