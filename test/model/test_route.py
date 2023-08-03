from ...src.model.route import Route


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
        # 无法添加loss差不多的节点
        route = Route()
        node_next = route.get_next()
        assert not route.add_node(node_next.speed_pre, node_next.loss_pre)
        pass

    def test_add_last(self):
        route = Route()
        assert route.get_next() is not None
        # 添加最后一个节点后，next节点为空
        assert route.add_node(1, 1)
        assert route.get_next() is None

        # 空节点时无法添加新节点
        assert not route.add_node(1, 0.5)
        pass
    pass
