from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiomysql

from .db import ConnExecutor, SqlManage

from ...configuration.rds import pool_manage


@asynccontextmanager
async def __transaction(conn: aiomysql.Connection):
    try:
        await conn.begin()
        yield
        await conn.commit()
    except Exception:
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
