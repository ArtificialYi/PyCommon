import pymysql
from typing import Generator
from contextlib import contextmanager
from pymysqlpool import ConnectionPool
from pymysql.cursors import SSDictCursor

from .base import ConnExecutorSync
from ..data.rds import RDSConfigData
from ...tool.map_tool import MapKeyGlobal


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
        print(f'db_conn事务异常:{type(e).__name__}|{e}')
        conn.rollback()
        raise
    pass


@contextmanager
def get_conn(pool: ConnectionPool, use_transaction: bool = False):
    with pool.get_connection(pre_ping=True) as conn:
        if not use_transaction:
            yield conn
            return

        with __transaction(conn):
            yield conn
            pass
        pass
    pass


@MapKeyGlobal(RDSConfigData.to_key)
def get_pool(data: RDSConfigData) -> ConnectionPool:  # pragma: no cover
    return ConnectionPool(
        size=1,
        pre_create_num=1,
        maxsize=data.max_conn,
        host=data.host,
        port=data.port,
        user=data.user,
        password=data.password,
        database=data.db,
        cursorclass=SSDictCursor,
    )


class MysqlManageSync:
    def __init__(self, data: RDSConfigData) -> None:
        self.__data = data
        pass

    def pool(self):
        return get_pool(self.__data)

    @contextmanager
    def __call__(self, use_transaction: bool = False) -> Generator[ConnExecutorSync, None, None]:
        with get_conn(self.pool(), use_transaction) as conn:
            yield ConnExecutorSync(conn)
        pass
    pass
