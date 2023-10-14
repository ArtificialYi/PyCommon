import sqlite3

from typing import Generator
from contextlib import contextmanager

from .base import ConnExecutorSync

from ..sqlite import dict_factory

from ...configuration.sync.log import LoggerLocal


@contextmanager
def __transaction(conn: sqlite3.Connection) -> Generator[None, None, None]:
    try:
        conn.execute('BEGIN')
        yield
        conn.execute('COMMIT')
    except BaseException as e:
        LoggerLocal.exception(e, f'db_conn事务异常:{type(e).__name__}|{e}')
        conn.execute('ROLLBACK') if isinstance(e, Exception) else None
        raise e


@contextmanager
def get_conn(db_name: str, use_transaction: bool) -> Generator[sqlite3.Connection, None, None]:
    with sqlite3.connect(db_name) as conn:
        conn.row_factory = dict_factory
        if not use_transaction:
            yield conn
            return

        with __transaction(conn):
            yield conn
        pass
    pass


class SqliteManageSync:
    def __init__(self, db_name: str) -> None:
        self.__db_name = db_name
        pass

    @contextmanager
    def __call__(self, use_transaction: bool = False) -> Generator[ConnExecutorSync, None, None]:
        with get_conn(self.__db_name, use_transaction) as conn:
            yield ConnExecutorSync(conn)
            pass
        pass
    pass
