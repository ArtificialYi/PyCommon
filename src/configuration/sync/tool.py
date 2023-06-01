from configparser import ConfigParser
import os


class ConfigTool:
    @staticmethod
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
