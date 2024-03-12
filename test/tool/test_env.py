import pytest
from ...src.tool.env_tool import EnvEnum


class TestEnv:
    def test_norm(self):
        """当前已有的环境
        """
        assert EnvEnum('TEST').value == 'TEST'
        assert EnvEnum('DEV').value == 'DEV'
        assert EnvEnum('PRE').value == 'PRE'
        assert EnvEnum('PROD').value == 'PROD'
        pass

    def test_err_lower(self):
        """无法用小写初始化
        """
        with pytest.raises(ValueError):
            EnvEnum('test')
            pass
        pass

    def test_err_none(self):
        """无法用不存在的环境初始化
        """
        with pytest.raises(ValueError):
            EnvEnum('QA')
            pass
        pass
    pass
