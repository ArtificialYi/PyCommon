from abc import abstractmethod

from .tool import ConfigTool, DCLGlobalAsync
from .env import ConfigEnv
from asyncinit import asyncinit
import aiomysql
from aiomysql import SSDictCursor


class DTConfig:
    def __init__(self, host: str, port: str, user: str, password: str, db: str) -> None:
        self.host = host
        self.port = int(port) if len(port) > 0 else 0
        self.user = user
        self.password = password
        self.db = db
        pass
    pass


@asyncinit
class DTConfigManage:
    @DCLGlobalAsync()
    async def __new__(cls) -> DTConfig:
        config_env = await ConfigEnv.config_env()
        config_default = await ConfigEnv.config_default()
        return DTConfig(
            ConfigTool.get_value('rds', 'host', config_default, config_env),
            ConfigTool.get_value('rds', 'port', config_default, config_env),
            ConfigTool.get_value('rds', 'user', config_default, config_env),
            ConfigTool.get_value('rds', 'password', config_default, config_env),
            ConfigTool.get_value('rds', 'db', config_default, config_env),
        )
    pass


@asyncinit
class DBPool:
    @DCLGlobalAsync()
    async def __new__(cls) -> aiomysql.Pool:
        config_db = await DTConfigManage()
        return await aiomysql.create_pool(**{
            'host': config_db.host,
            'port': config_db.port,
            'user': config_db.user,
            'password': config_db.password,
            'db': config_db.db,
            'cursorclass': SSDictCursor,
        })
    pass


class NormAction:
    @abstractmethod
    async def action(self, cursor: aiomysql.SSDictCursor):
        pass
    pass


class IterAction:
    @abstractmethod
    async def action(self, cursor: aiomysql.SSDictCursor):
        yield
    pass
