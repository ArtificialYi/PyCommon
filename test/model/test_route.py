from ...src.model.route import ArgsLatitude, Route


class TestRoute:
    def test_init(self):
        # 初始化route
        route = Route()
        node_next = route.get_next()
        assert not node_next.is_ok
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
        # 无法添加next以外的节点
        route = Route()
        node_next = route.get_next()
        node_not_next = ArgsLatitude(1, 2, 2)
        assert node_next is not None and node_next.al != node_not_next
        assert not route.add_node(node_not_next, None, None)

        # 无法添加loss差不多的节点
        assert not route.add_node(node_next.al, node_next.speed_pre, node_next.loss_pre)
        pass
    pass
