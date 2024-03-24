from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiosqlite

from .base import ActionNorm, ConnExecutor

from ..sqlite import dict_factory

from ...configuration.norm.log import LoggerLocal


# async def __rollback_unit(conn: aiosqlite.Connection):
#     """执行SQL回滚
#     抛出非业务异常
#     """
#     try:
#         await conn.execute('ROLLBACK')
#     except BaseException as e:
#         await LoggerLocal.exception(e, f'rollback失败:{type(e).__name__}|{e}')
#         ExceptTool.raise_not_exception(e)
#         pass
#     pass


@asynccontextmanager
async def __transaction(conn: aiosqlite.Connection):
    try:
        await conn.execute('BEGIN;')
        yield conn
        await conn.execute('COMMIT;')
    except BaseException as e:
        await LoggerLocal.exception(e, f'db_conn事务异常:{type(e).__name__}|{e}')
        await conn.execute('ROLLBACK;') if isinstance(e, Exception) else None
        raise e


@asynccontextmanager
async def get_conn(db_name: str, use_transaction: bool = False) -> AsyncGenerator[aiosqlite.Connection, None]:
    async with aiosqlite.connect(db_name) as conn:
        conn.row_factory = dict_factory
        await conn.execute('PRAGMA journal_mode=WAL;')
        if not use_transaction:
            yield conn
            return

        async with __transaction(conn):
            yield conn
            pass
        pass
    pass


class SqliteManage:
    def __init__(self, db_name: str) -> None:
        self.__db_name = db_name
        pass

    @asynccontextmanager
    async def __call__(self, use_transaction: bool = False) -> AsyncGenerator[ConnExecutor, None]:
        async with get_conn(self.__db_name, use_transaction) as conn:
            yield ConnExecutor(conn)
        pass
    pass


class ServiceNorm:
    @staticmethod
    async def table_exist(sql_manage: SqliteManage, table_name: str) -> bool:
        async with sql_manage() as conn:
            row = await conn.row_one(ActionNorm.table_exist(table_name))
            return row['COUNT'] > 0
    pass
