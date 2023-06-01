import os

from ...src.configuration.norm.env import COMMON_ROOT
from ...src.tool.config_tool import ConfigBase


class TestConfigBase:
    def test_exists(self):
        ini_pytest = os.path.join(COMMON_ROOT, 'tox.ini')
        config = ConfigBase.get_config(ini_pytest)
        assert len(config.sections()) == 2
        assert ConfigBase.get_value('pytest', 'asyncio_mode', config) == 'auto'
        pass

    def test_not_exists(self):
        ini_exists = os.path.join(COMMON_ROOT, 'not_exists.ini')
        config = ConfigBase.get_config(ini_exists)
        assert len(config.sections()) == 0
        pass
    pass
