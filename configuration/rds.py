from abc import abstractmethod
from typing import Dict, Tuple, Union
from .tool import ConfigTool
import pymysql
from .env import ConfigEnv
from dbutils.pooled_db import PooledDB
from pymysql.connections import Connection
from pymysql.cursors import Cursor


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
    def config(cls) -> DBConfig:
        if cls.__CONFIG is not None:
            return cls.__CONFIG

        config_env = ConfigEnv.config_env()
        config_default = ConfigEnv.config_default()
        cls.__CONFIG = DBConfig(
            ConfigTool.get_value('rds', 'host', config_default, config_env),
            ConfigTool.get_value('rds', 'port', config_default, config_env),
            ConfigTool.get_value('rds', 'user', config_default, config_env),
            ConfigTool.get_value('rds', 'password', config_default, config_env),
            ConfigTool.get_value('rds', 'mincached', config_default, config_env),
            ConfigTool.get_value('rds', 'ping', config_default, config_env),
        )
        return cls.__CONFIG
    pass


class DBPool:
    """构造DB对应的连接池
    1. 开放 从连接池中获取conn
    """
    def __init__(self, db_name: str) -> None:
        config_db = DBConfigManage.config()
        self.__pool = PooledDB(creator=pymysql, **{
            'host': config_db.host,
            'port': config_db.port,
            'user': config_db.user,
            'password': config_db.password,
            'db': db_name,
            'mincached': config_db.mincached,
            'blocking': True,
            'ping': config_db.ping,
        })
        pass

    def get_conn(self) -> Connection:
        """线程之间不共享连接
        """
        return self.__pool.connection(shareable=False)  # type: ignore
    pass


class ActionDB:
    @abstractmethod
    def __new__(cls, conn: Connection, cursor: Cursor, sql: str, args) -> Union[int, Tuple[Dict]]:
        pass
    pass
