from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiosqlite


@asynccontextmanager
async def __transaction(conn: aiosqlite.Connection):
    try:
        await conn.execute('BEGIN')
        yield conn
        await conn.execute('COMMIT')
    except Exception as e:
        await conn.execute('ROLLBACK')
        raise e


@asynccontextmanager
async def get_conn(db_name: str, use_transaction: bool = False) -> AsyncGenerator[aiosqlite.Connection, None]:
    async with aiosqlite.connect(db_name) as conn:
        if not use_transaction:
            yield conn
            return

        async with __transaction(conn):
            yield conn
            pass
        pass
    pass


class ActionExec:
    def __init__(self, sql: str, *args) -> None:
        self.__sql = sql
        self.__args = args
        pass

    async def __call__(self, cursor: aiosqlite.Cursor) -> int:
        cursor_res = await cursor.execute(self.__sql, self.__args)
        return cursor_res.rowcount
    pass


class ActionIter:
    def __init__(self, sql: str, *args) -> None:
        self.__sql = sql
        self.__args = args
        pass

    async def __call__(self, cursor: aiosqlite.Cursor) -> AsyncGenerator[aiosqlite.Row, None]:
        await cursor.execute(self.__sql, self.__args)
        while (row := await cursor.fetchone()) is not None:
            yield row
            pass
        pass
    pass


class ConnExecutor:
    def __init__(self, conn: aiosqlite.Connection) -> None:
        self.__conn = conn
        pass

    async def exec(self, coro: ActionExec) -> int:
        async with self.__conn.cursor() as cursor:
            return await coro(cursor)

    async def iter(self, gen: ActionIter) -> AsyncGenerator[aiosqlite.Row, None]:
        async with self.__conn.cursor() as cursor:
            async for row in gen(cursor):
                yield row
                pass
            pass
        pass
    pass


class SqliteManage:
    def __init__(self, db_name: str) -> None:
        self.__db_name = db_name
        pass

    @asynccontextmanager
    async def __call__(self, use_transaction: bool = False) -> AsyncGenerator[ConnExecutor, None]:
        try:
            async with get_conn(self.__db_name, use_transaction) as conn:
                yield ConnExecutor(conn)
            pass
        except Exception as e:
            # TODO: 这里需要记录日志
            print(e)
            pass
        pass
    pass
