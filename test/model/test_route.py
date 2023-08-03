from ...src.model.route import ArgsLatitude, Route


class TestRoute:
    def test_init(self):
        # 初始化route
        route = Route()
        node_next = route.get_next()
        assert node_next.al.length == 1
        assert node_next.al.layer == 1
        assert node_next.al.hidden == 2
        assert node_next.speed_pre == float('inf')
        assert node_next.loss_pre == float('inf')
        assert node_next.speed_now is None
        assert node_next.loss_now is None

        # node_next非pop
        assert route.get_next() == node_next
        pass

    def test_add_fail_norm(self):
        # 无法刷新loss差不多的节点
        route = Route()
        node_next = route.get_next()
        assert not route.refresh_node(node_next.speed_pre, node_next.loss_pre)
        pass

    def test_add_last(self):
        route = Route()
        assert route.get_next() is not None
        # 刷新最后一个节点后，next节点为空
        assert route.refresh_node(1, 1)
        assert route.get_next() is None

        # 空节点时无法刷新新节点
        assert not route.refresh_node(1, 0.5)
        pass

    def test_add_norm(self):
        route = Route(length_max=2, layer_max=4)
        node_tmp = route.get_next()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 2)

        # 刷新1，1，2节点，下一个节点为2，1，2
        assert route.refresh_node(300, 1)
        node_tmp = route.get_next()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(2, 1, 2)

        # 刷新2，1，2节点，下一个节点为1，1，4（用以测试length字段，不会再出现）
        assert route.refresh_node(50, 0.3)
        node_tmp = route.get_next()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 4)

        # 刷新1，1，4节点，下一个节点为1，2, 4
        assert route.refresh_node(250, 0.9)
        node_tmp = route.get_next()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 2, 4)

        # 刷新1，2，4节点，下一个节点为1，1，8
        assert route.refresh_node(100, 0.5)
        node_tmp = route.get_next()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 8)

        # 刷新1，1，8节点，下一个节点为1，1, 16
        assert route.refresh_node(200, 0.8)
        node_tmp = route.get_next()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 1, 16)

        # 刷新1，1，16节点，下一个节点为1，2, 8（此时2，16为无效节点）
        assert route.refresh_node(150, 0.4)
        node_tmp = route.get_next()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 2, 8)

        # 刷新1，2，8节点，下一个节点为1，2，16(此时2，8节点不如1，16节点)
        assert route.refresh_node(90, 0.45)
        node_tmp = route.get_next()
        assert node_tmp is not None and node_tmp.al == ArgsLatitude(1, 2, 16)
        pass
    pass
