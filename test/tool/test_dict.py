import pytest
from ...src.tool.dict_tool import DictTool, KeyNotExistError


class TestDictTool:
    def test_keys_exist(self):
        assert DictTool.assert_keys_exist({}, []) is None
        assert DictTool.assert_keys_exist({'tmp': ''}, ['tmp']) is None
        assert DictTool.assert_keys_exist({'a': 0, 'b': 1}, 'ab') is None
        with pytest.raises(KeyNotExistError):
            DictTool.assert_keys_exist({}, ['tmp'])
            pass
        pass

    def test_swap_value(self):
        data_tmp = {'a': 0, 'b': 1}
        with DictTool.swap_value(data_tmp, 'a', 1) as data:
            assert data == data_tmp
            assert data['a'] == 1
            assert data_tmp['a'] == 1
            pass
        assert data_tmp['a'] == 0
        pass
    pass
