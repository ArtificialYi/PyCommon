import pytest
from ...src.tool.dict_tool import DictTool, KeyNotExistError


class TestDictTool:
    def test_err(self):
        assert DictTool.key_exist_raise({'': 0}, '') is None
        with pytest.raises(KeyNotExistError):
            DictTool.key_exist_raise({}, 'tmp')
            pass
        pass
    pass
