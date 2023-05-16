from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiomysql

from ...configuration.log import LoggerLocal
from .db import ConnExecutor, SqlManage
from ...configuration.rds import pool_manage


# async def __rollback_unit(conn: aiomysql.Connection):
#     """执行SQL回滚
#     抛出非业务异常
#     """
#     try:
#         await conn.rollback()
#     except BaseException as e:
#         await LoggerLocal.exception(e, f'rollback失败:{type(e).__name__}|{e}')
#         ExceptTool.raise_not_exception(e)
#         pass
#     pass


@asynccontextmanager
async def __transaction(conn: aiomysql.Connection):
    """事务开启与关闭
    当遇到业务异常时，执行回滚
    """
    try:
        await conn.begin()
        yield
        await conn.commit()
    except BaseException as e:
        await LoggerLocal.exception(e, f'db_conn事务异常:{type(e).__name__}|{e}')
        await conn.rollback()
        raise
    pass


@asynccontextmanager
async def get_conn(pool: aiomysql.Pool, use_transaction: bool = False):
    async with pool.acquire() as conn:
        if not use_transaction:
            yield conn
            return

        async with __transaction(conn):
            yield conn
            pass
        pass
    pass


class MysqlManage(SqlManage):
    def __init__(self, flag: str):
        self.__flag = flag
        self.__pool = None
        pass

    async def __get_pool(self):
        if self.__pool is not None:
            return self.__pool
        # TODO: 这里的pool应该从全局获取
        self.__pool = await pool_manage(self.__flag)
        return self.__pool

    @asynccontextmanager
    async def __call__(self, use_transaction: bool = False) -> AsyncGenerator[ConnExecutor, None]:
        async with get_conn(await self.__get_pool(), use_transaction) as conn:
            yield ConnExecutor(conn)
        pass
    pass
