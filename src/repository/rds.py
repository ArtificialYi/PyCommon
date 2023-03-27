from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiomysql

from .db import ActionExec, ActionIter

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


class ConnExecutor:
    def __init__(self, conn: aiomysql.Connection) -> None:
        self.__conn = conn
        pass

    async def exec(self, coro: ActionExec) -> int:
        async with self.__conn.cursor() as cursor:
            return await coro(cursor)

    async def iter(self, gen: ActionIter) -> AsyncGenerator[dict, None]:
        async with self.__conn.cursor() as cursor:
            async for row in gen(cursor):
                yield row
                pass
            pass
        pass
    pass


@asyncinit
class MysqlManage:
    async def __init__(self, flag: str):
        # TODO: 这里的pool应该从全局获取
        self.__pool = await pool_manage(flag)
        pass

    @asynccontextmanager
    async def __call__(self, use_transaction: bool = False) -> AsyncGenerator[ConnExecutor, None]:
        try:
            async with get_conn(self.__pool, use_transaction) as conn:
                yield ConnExecutor(conn)
            pass
        except Exception as e:
            # TODO: 这里需要记录日志
            raise e
        pass
    pass
