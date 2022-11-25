from collections import OrderedDict
from ...src.tool.dict_tool import DictTool


class TestDictTool:
    def test(self):
        key0 = 'tmp0'
        key1 = 'tmp1'
        keys = [key0, key1]
        # 非全部存在
        assert not DictTool.keys_exists({key0: 1}, keys)

        # 全部存在，但是存在映射为None
        assert not DictTool.keys_exists({
            key0: 1,
            key1: None,
        }, keys)

        # 全部存在 & 全不为None
        assert DictTool.keys_exists({
            key0: 1,
            key1: 0,
        }, keys)

        # 非纯dict也等同
        assert DictTool.keys_exists(OrderedDict([
            (key0, 0),
            (key1, 1),
        ]), keys)
        pass
    pass
