from typing import Any, AsyncGenerator, Iterable, Optional, Union
import aiomysql
import aiosqlite

from ...tool.sql_tool import Mysql2Other


class ActionExec:
    def __init__(self, sql: str, args: Optional[Iterable[Any]] = None) -> None:
        self.__sql = sql
        self.__args = args if args is not None else []
        pass

    async def __call__(self, cursor: Union[aiomysql.SSDictCursor, aiosqlite.Cursor]) -> int:
        sql = self.__sql if isinstance(cursor, aiomysql.SSDictCursor) else Mysql2Other.sqlite(self.__sql)
        await cursor.execute(sql, self.__args)
        return cursor.rowcount
    pass


class ActionIter:
    def __init__(self, sql: str, args: Optional[Iterable[Any]] = None) -> None:
        self.__sql = sql
        self.__args = args if args is not None else []
        pass

    async def __call__(self, cursor: Union[aiomysql.SSDictCursor, aiosqlite.Cursor]) -> AsyncGenerator[dict, None]:
        sql = self.__sql if isinstance(cursor, aiomysql.SSDictCursor) else Mysql2Other.sqlite(self.__sql)
        await cursor.execute(sql, self.__args)
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
