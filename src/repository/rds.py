import asyncio
from contextlib import asynccontextmanager
from typing import AsyncGenerator, Union
import aiomysql

from ...configuration.rds import NormAction, IterAction


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


class DBExecutorSafe:
    """使用说明
    1. 异步初始化
    2. 放入async with来传递conn和事务
    """
    def __init__(self, pool: aiomysql.Pool, use_transaction: bool = False):
        self.__pool = pool
        self.__use = use_transaction
        self.__lock = asyncio.Lock()
        self.__conn: Union[aiomysql.Connection, None] = None
        pass

    async def execute(self, action: NormAction):
        if self.__conn is None:
            raise Exception('尚未获取conn')

        async with self.__conn.cursor() as cursor:
            return await action.action(cursor)

    async def iter_opt(self, action: IterAction):
        if self.__conn is None:
            raise Exception('尚未获取conn')

        async with self.__conn.cursor() as cursor:
            async for row in action.action(cursor):
                yield row
                pass
            pass
        pass

    async def __aenter__(self):
        await self.__lock.acquire()
        self.__gen = get_conn(self.__pool, self.__use)
        self.__conn = await self.__gen.__aenter__()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        if exc_value is not None:
            # TODO: 需要留下日志
            print(exc_value)
        await self.__gen.__aexit__(exc_type, exc_value, traceback)
        self.__conn = None
        self.__lock.release()
        return True
    pass


class ExecuteAction(NormAction):
    def __init__(self, sql: str, *args) -> None:
        self.__sql = sql
        self.__args = args
        pass

    async def action(self, cursor: aiomysql.SSDictCursor) -> int:
        return await cursor.execute(self.__sql, self.__args)
    pass


class FetchAction(IterAction):
    def __init__(self, sql: str, *args) -> None:
        self.__sql = sql
        self.__args = args
        pass

    async def action(self, cursor: aiomysql.SSDictCursor) -> AsyncGenerator:
        await cursor.execute(self.__sql, self.__args)
        while (row := await cursor.fetchone()) is not None:
            yield row
            pass
        pass
    pass
