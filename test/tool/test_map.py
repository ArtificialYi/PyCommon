
from ...src.tool.map_tool import Map, MapKeyOne


class TestMap:
    def test_get_value_with_args(self):
        m = Map(lambda x, y: x + y)
        assert m.get_value(1, 1, 2) == 3
        assert m.get_value(2, 2, 3) == 5
        assert m.get_value(3, 3, 4) == 7
        pass

    def test_get_value_with_kwds(self):
        m = Map(lambda x, y: x + y)
        assert m.get_value(1, 1, y=2) == 3
        assert m.get_value(2, 2, y=3) == 5
        assert m.get_value(3, 3, y=4) == 7
        pass

    def test_get_value_with_args_and_kwds(self):
        m = Map(lambda x, y, z: x + y + z)
        assert m.get_value(1, 1, 2, z=3) == 6
        assert m.get_value(2, 2, 3, z=4) == 9
        assert m.get_value(3, 3, 4, z=5) == 12
        pass


class TestMapKeyOne:
    def test_get_value_with_key_one(self):
        m = MapKeyOne(lambda x: x)
        assert m.get_value(1) == 1
        assert m.get_value(2) == 2
        assert m.get_value(3) == 3
        pass

    def test_get_value_with_key_one_and_args(self):
        m = MapKeyOne(lambda x, y: x + y)
        assert m.get_value(1, 2) == 3
        assert m.get_value(2, 3) == 5
        assert m.get_value(3, 4) == 7
        pass

    def test_get_value_with_key_one_and_kwds(self):
        m = MapKeyOne(lambda x, y: x + y)
        assert m.get_value(1, y=2) == 3
        assert m.get_value(2, y=3) == 5
        assert m.get_value(3, y=4) == 7
        pass

    def test_get_value_with_key_one_and_args_and_kwds(self):
        m = MapKeyOne(lambda x, y, z: x + y + z)
        assert m.get_value(1, 2, z=3) == 6
        assert m.get_value(2, 3, z=4) == 9
        assert m.get_value(3, 4, z=5) == 12
        pass
    pass
