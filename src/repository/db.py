from contextlib import asynccontextmanager
from typing import AsyncGenerator, Union
import aiomysql
import aiosqlite


class ActionExec:
    def __init__(self, sql: str, *args) -> None:
        self.__sql = sql
        self.__args = args
        pass

    async def __call__(self, cursor: Union[aiomysql.SSDictCursor, aiosqlite.Cursor]) -> int:
        await cursor.execute(self.__sql, self.__args)
        return cursor.rowcount
    pass


class ActionIter:
    def __init__(self, sql: str, *args) -> None:
        self.__sql = sql
        self.__args = args
        pass

    async def __call__(self, cursor: Union[aiomysql.SSDictCursor, aiosqlite.Cursor]) -> AsyncGenerator[dict, None]:
        await cursor.execute(self.__sql, self.__args)
        while (row := await cursor.fetchone()) is not None:
            yield dict(row)
            pass
        pass
    pass


class ConnExecutor:
    def __init__(self, conn: Union[aiomysql.Connection, aiosqlite.Connection]) -> None:
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


class SqlManage:
    @asynccontextmanager
    async def __call__(self, *args, **kwds) -> AsyncGenerator[ConnExecutor, None]:
        yield ConnExecutor(None)  # type: ignore
        pass
    pass
