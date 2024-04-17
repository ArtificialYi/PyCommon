from configparser import ConfigParser
import os
import aiofiles

from ...tool.base import BaseTool

from ...tool.map_tool import MapKeyGlobal


class ConfigTool:
    @staticmethod
    @MapKeyGlobal(BaseTool.return_self)
    async def get_config(path: str):
        config = ConfigParser()
        if os.path.exists(path):
            async with aiofiles.open(path, 'r') as config_file:
                str_config = await config_file.read()
                config.read_string(str_config)
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
