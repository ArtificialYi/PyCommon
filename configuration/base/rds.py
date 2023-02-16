from .base import ConfigBase
from .env import ConfigEnv


class DBConfig:
    def __init__(self, host: str, port: str, user: str, password: str, mincached: str, ping: str) -> None:
        self.host = host
        self.port = int(port) if len(port) > 0 else 0
        self.user = user
        self.password = password
        self.mincached = int(mincached) if len(mincached) > 0 else 0
        self.ping = int(ping) if len(ping) > 0 else 0
        pass
    pass


class DBConfigManage:
    __CONFIG = None

    @classmethod
    def config(cls):
        if cls.__CONFIG is not None:
            return cls.__CONFIG

        config_env = ConfigEnv.config_env()
        config_default = ConfigEnv.config_default()
        cls.__CONFIG = DBConfig(
            ConfigBase.get_value('rds', 'host', config_default, config_env),
            ConfigBase.get_value('rds', 'port', config_default, config_env),
            ConfigBase.get_value('rds', 'user', config_default, config_env),
            ConfigBase.get_value('rds', 'password', config_default, config_env),
            ConfigBase.get_value('rds', 'mincached', config_default, config_env),
            ConfigBase.get_value('rds', 'ping', config_default, config_env),
        )
        return cls.__CONFIG
    pass
