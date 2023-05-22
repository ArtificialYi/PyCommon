import pytest
from ...src.tool.dict_tool import DictTool, KeyNotExistError


class TestDictTool:
    def test_err(self):
        assert DictTool.assert_keys_exist({}, []) is None
        assert DictTool.assert_keys_exist({'tmp': ''}, ['tmp']) is None
        assert DictTool.assert_keys_exist({'a': 0, 'b': 1}, 'ab') is None
        with pytest.raises(KeyNotExistError):
            DictTool.assert_keys_exist({}, ['tmp'])
            pass
        pass
    pass
