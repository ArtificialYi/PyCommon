from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiomysql

from .db import ConnExecutor, SqlManage

from ...configuration.rds import pool_manage
from asyncinit import asyncinit


@asynccontextmanager
async def __transaction(conn: aiomysql.Connection):
    try:
        await conn.begin()
        yield
        await conn.commit()
    except Exception as e:
        await conn.rollback()
        raise e
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


@asyncinit
class MysqlManage(SqlManage):
    async def __init__(self, flag: str):
        # TODO: 这里的pool应该从全局获取
        self.__pool = await pool_manage(flag)
        pass

    @asynccontextmanager
    async def __call__(self, use_transaction: bool = False) -> AsyncGenerator[ConnExecutor, None]:
        async with get_conn(self.__pool, use_transaction) as conn:
            yield ConnExecutor(conn)
        pass
    pass
