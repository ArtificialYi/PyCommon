from abc import abstractmethod
from typing import AsyncGenerator

from .tool import ConfigTool, DCLGlobalAsync
from .env import ConfigEnv
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


@DCLGlobalAsync()
async def config_manage(flag: str):
    config_env = await ConfigEnv.config_env()
    config_default = await ConfigEnv.config_default()
    args = (
        ConfigTool.get_value(flag, 'host', config_default, config_env),
        ConfigTool.get_value(flag, 'port', config_default, config_env),
        ConfigTool.get_value(flag, 'user', config_default, config_env),
        ConfigTool.get_value(flag, 'password', config_default, config_env),
        ConfigTool.get_value(flag, 'db', config_default, config_env),
    )
    return DTConfig(*args)


@DCLGlobalAsync()
async def pool_manage(flag: str):
    config_db = await config_manage(flag)
    return await aiomysql.create_pool(**{
        'host': config_db.host,
        'port': config_db.port,
        'user': config_db.user,
        'password': config_db.password,
        'db': config_db.db,
        'cursorclass': SSDictCursor,
    })


class NormAction:
    @abstractmethod
    async def action(self, cursor: aiomysql.SSDictCursor) -> int:
        pass
    pass


class IterAction:
    @abstractmethod
    async def action(self, cursor: aiomysql.SSDictCursor) -> AsyncGenerator:
        yield
    pass
