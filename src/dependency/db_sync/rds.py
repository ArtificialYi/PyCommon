from contextlib import contextmanager
from typing import Generator
import pymysql
from dbutils.pooled_db import PooledDB

from ...tool.map_tool import MapKey
from .base import ConnExecutorSync
from ...configuration.sync.log import LoggerLocal


@contextmanager
def __transaction(conn: pymysql.Connection):
    """事务开启与关闭
    当遇到业务异常时，执行回滚
    """
    try:
        conn.begin()
        yield
        conn.commit()
    except BaseException as e:
        LoggerLocal.exception(e, f'db_conn事务异常:{type(e).__name__}|{e}')
        conn.rollback()
        raise
    pass


@contextmanager
def __pool2conn(pool: PooledDB):
    """连接池获取连接与释放
    """
    conn = pool.connection(False)
    try:
        yield conn
    finally:
        conn.close()
        pass
    pass


@contextmanager
def get_conn(pool: PooledDB, use_transaction: bool = False):
    with __pool2conn(pool) as conn:
        if not use_transaction:
            yield conn
            return

        with __transaction(conn):
            yield conn
        pass
    pass


class RDSConfigData:
    FIELDS = ('host', 'port', 'user', 'password', 'db', 'max_conn')

    def to_key(self):  # pragma: no cover
        return f'{self.host}:{self.port}:{self.user}:{self.password}:{self.db}:{self.max_conn}'

    def __init__(self, host: str, port: str, user: str, password: str, db: str, max_conn: str) -> None:
        self.host = host
        self.port = int(port) if len(port) > 0 else 0
        self.user = user
        self.password = password
        self.db = db
        self.max_conn = int(max_conn)
        pass
    pass


@MapKey(RDSConfigData.to_key)
def get_pool(data: RDSConfigData) -> PooledDB:  # pragma: no cover
    return PooledDB(
        creator=pymysql,
        maxconnections=data.max_conn,
        host=data.host,
        port=data.port,
        db=data.db,
        user=data.user,
        password=data.password,
        blocking=True,
    )


class MysqlManageSync:
    def __init__(self, data: RDSConfigData) -> None:
        self.__data = data
        pass

    def pool(self) -> PooledDB:
        return get_pool(self.__data)

    @contextmanager
    def __call__(self, use_transaction: bool = False) -> Generator[ConnExecutorSync, bool, None]:
        with get_conn(self.pool(), use_transaction) as conn:
            yield ConnExecutorSync(conn)
        pass
    pass
