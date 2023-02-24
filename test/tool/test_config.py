from configparser import ConfigParser
import os

from ...configuration.env import COMMON_ROOT
from ...src.tool.config_tool import ConfigBase


class TestConfigBase:
    def test(self):
        ini_pytest = os.path.join(COMMON_ROOT, 'pytest.ini')
        config = ConfigBase.get_config(ini_pytest)
        assert type(config) == ConfigParser
        assert ConfigBase.get_value('pytest', 'asyncio_mode', config) == 'auto'
        pass
    pass
