import threading
from typing import Dict
import pymysql
from .base import ConfigBase
from .env import ConfigEnv
from dbutils.pooled_db import PooledDB
from pymysql.cursors import SSDictCursor
from pymysql.connections import Connection


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
            ConfigBase.get_value('rds', 'host', config_default, config_env),
            ConfigBase.get_value('rds', 'port', config_default, config_env),
            ConfigBase.get_value('rds', 'user', config_default, config_env),
            ConfigBase.get_value('rds', 'password', config_default, config_env),
            ConfigBase.get_value('rds', 'mincached', config_default, config_env),
            ConfigBase.get_value('rds', 'ping', config_default, config_env),
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
        self.__lock = threading.Lock()
        pass

    def get_conn(self) -> Connection:
        """线程之间不共享连接
        """
        return self.__pool.connection(shareable=False)  # type: ignore
    pass


class DBBase:
    DB_NAME = ''
    __POOL_MAP: Dict[str, DBPool] = dict()

    @classmethod
    def get_pool(cls, db_name: str):
        if DBBase.__POOL_MAP.get(cls.DB_NAME, None) is not None:
            return DBBase.__POOL_MAP[cls.DB_NAME]

        DBBase.__POOL_MAP[cls.DB_NAME] = DBPool(db_name)
        return DBBase.__POOL_MAP[cls.DB_NAME]

    @classmethod
    def _affected_more(cls, sql: str, args) -> int:
        with (
            DBBase.get_pool(cls.DB_NAME).get_conn() as conn,
            conn.cursor(SSDictCursor) as cursor,
        ):
            conn.begin()
            effected_rows = cursor.execute(sql, args)
            if not isinstance(effected_rows, int):
                conn.rollback()
                raise Exception(f'异常SQL调用:{sql}')
            conn.commit()
            return effected_rows

    @classmethod
    def _force_commit(cls, sql: str, args):
        with (
            DBBase.get_pool(cls.DB_NAME).get_conn() as conn,
            conn.cursor(SSDictCursor) as cursor,
        ):
            conn.begin()
            effected_rows = cursor.execute(sql, args)
            conn.commit()
            return effected_rows

    @classmethod
    def _no_transaction(cls, sql: str, args):
        with DBBase.get_pool(cls.DB_NAME).get_conn().cursor(SSDictCursor) as cursor:
            return cursor.execute(sql, args)
    pass
