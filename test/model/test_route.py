from ...src.model.route import ArgsLatitude, Route, TrainUnit


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

        assert a.get_next() is None
        pass

    def test_add_norm(self):
        a = Route()
        assert not a.get_next().is_ok
        assert a.get_next() is None

        # 尚未完成节点无法添加
        a.add_note(TrainUnit(ArgsLatitude(1, 1, 2), 1, 1))
        assert a.get_next() is None
        pass
    pass
