from configparser import ConfigParser
import os

from ...tool.base import BaseTool

from ...tool.map_tool import MapKeyGlobal


class ConfigTool:
    @staticmethod
    @MapKeyGlobal(BaseTool.return_self)
    def get_config(path: str):
        config = ConfigParser()
        if os.path.exists(path):
            config.read(path)
            pass
        return config

    @staticmethod
    def get_value(
        section: str, option: str, *config_lst: ConfigParser, default=''
    ):
        res = default
        for config in config_lst:
            res = config.get(section, option, fallback=res)
            pass
        return res
    pass
