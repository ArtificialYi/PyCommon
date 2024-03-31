import pytest

from ...src.model.route import ArgsLatitudeManage, ArgsLatitude, RouteManage


class TestData:
    def test_data_eq(self):
        a = ArgsLatitude(hidden=2, layer=1, loss=3)
        b = ArgsLatitude(hidden=2, layer=1, loss=3)
        assert a == b

        c = ArgsLatitude(hidden=2, layer=1, loss=4)
        assert a == c

    def test_data_hash(self):
        a = ArgsLatitude(hidden=2, layer=1, loss=3)
        b = ArgsLatitude(hidden=2, layer=1, loss=3)
        assert hash(a) == hash(b)
        assert len({a, b}) == 1

        c = ArgsLatitude(hidden=2, layer=1, loss=4)
        assert hash(a) == hash(c)
        assert len({a, c}) == 1

        d = ArgsLatitude(layer=1, hidden=3, loss=3)
        assert hash(a) != hash(d)
        assert len({a, d}) == 2

    def test_data_err(self):
        with pytest.raises(ValueError):
            ArgsLatitude(hidden=2, layer=2)
            pass
        pass

    def test_data_next(self):
        a = ArgsLatitude(hidden=2, layer=1)
        # layer=2, hidden=2 不存在
        assert len([_ for _ in a.iter_next(4)]) == 1
        assert len([_ for _ in a.iter_next(3)]) == 0
        assert len([_ for _ in a.iter_next(2)]) == 0

        b = ArgsLatitude(hidden=4, layer=1)
        assert len([_ for _ in b.iter_next(4)]) == 1
        assert len([_ for _ in b.iter_next(8)]) == 2
        pass

    def test_data_pre(self):
        a = ArgsLatitude(hidden=4, layer=2)
        # layer=2, hidden=2无法通过基础校验
        assert len([_ for _ in a.iter_pre(4)]) == 1
        # layer=1, hidden=4在hidden_min为8的情况下,无法找到
        assert len([_ for _ in a.iter_pre(8)]) == 0

        b = ArgsLatitude(hidden=8, layer=2)
        assert len([_ for _ in b.iter_pre(8)]) == 1
        assert len([_ for _ in b.iter_pre(4)]) == 2

        c = ArgsLatitude(hidden=4, layer=1)
        assert len([_ for _ in c.iter_pre(4)]) == 0
        assert len([_ for _ in c.iter_pre(2)]) == 1
        pass

    def test_order(self):
        data_lst = sorted([
            ArgsLatitude(hidden=4, layer=2, loss=10),
            ArgsLatitude(hidden=8, layer=1, loss=9),
            ArgsLatitude(hidden=4, layer=1, loss=9),
        ], key=ArgsLatitude.key_sorted)
        # loss大，先出
        assert data_lst[0] == ArgsLatitude(hidden=4, layer=2, loss=10)
        # hidden小，先出
        assert data_lst[1] == ArgsLatitude(hidden=4, layer=1, loss=9)
        pass
    pass


class TestDataManage:
    def test_create(self):
        a = ArgsLatitude(hidden=2, layer=1, loss=3)
        b = ArgsLatitude(hidden=2, layer=1, loss=3)
        assert id(a) != id(b)

        manage = ArgsLatitudeManage(2)

        c = manage.create(hidden=2, layer=1, loss=4)
        assert a == c
        assert hash(a) == hash(c)
        assert len({a, c}) == 1
        assert c.loss == 4

        d = manage.create(hidden=2, layer=1, loss=3)
        assert id(c) == id(d)
        assert c.loss == d.loss == 3

        e = manage.create(hidden=2, layer=1, loss=5)
        assert id(c) == id(e)
        assert e.loss == 3
        pass

    def test_next(self):
        a = ArgsLatitude(hidden=2, layer=1, loss=3)

        manage = ArgsLatitudeManage(4)

        assert manage.get_next(a, 4) is None
        assert manage.get_next(a, 3) is None
        assert len(manage.get_next(a, 2)) == 1
        pass
    pass


class TestRoute:
    def test_pop(self):
        # pop的最低条件：hidden_min>=2
        with pytest.raises(ValueError):
            RouteManage(1, 4).pop()
            pass

        route = RouteManage(2, 4)
        assert route.pop() == ArgsLatitude(hidden=2, layer=1)
        assert route.pop() is None
        pass

    def test_push(self):
        route = RouteManage(8, 32)
        unit = ArgsLatitude(hidden=8, layer=1)

        a = route.pop()
        assert a == unit
        # 必须是pop出来的那个对象才能推入
        with pytest.raises(Exception):
            route.push(unit, float('inf'))
            pass
        assert not route.push(a, float('inf'))

        assert route.pop() is None
        assert route.push(a, 10)

        # loss一样，hidden小，先出
        b = route.pop()
        assert b == ArgsLatitude(hidden=8, layer=2)
        assert b.loss == 10

        assert route.push(b, 9)

        # loss大，先出
        c = route.pop()
        assert c == ArgsLatitude(hidden=16, layer=1)
        assert c.loss == 10
        pass
    pass
