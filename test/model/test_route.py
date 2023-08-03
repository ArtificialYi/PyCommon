from ...src.model.route import Route


class TestRoute:
    def test_init(self):
        a = Route()
        b = a.get_next()
        assert not b.is_ok
        assert b.al.length == 1
        assert b.al.layer == 1
        assert b.al.hidden == 2
        assert b.speed_pre == float('inf')
        assert b.loss_pre == float('inf')
        assert b.speed_now is None
        assert b.loss_now is None

        assert a.get_next() == b
        pass

    def test_add_norm(self):
        pass
    pass
