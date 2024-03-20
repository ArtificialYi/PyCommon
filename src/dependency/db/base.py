from typing import Any, AsyncGenerator, Iterable, Optional, Union
import aiomysql
import aiosqlite

from ...exception.db import MultipleResultsFound

from ...tool.sql_tool import SQLTool


class SqlConv:
    def __init__(self, cursor: aiomysql.SSDictCursor | aiosqlite.Cursor) -> None:
        self.__conv = SQLTool.to_mysql if isinstance(cursor, aiomysql.SSDictCursor) else SQLTool.to_sqlite
        pass

    def __call__(self, sql: str) -> str:
        return self.__conv(sql)
    pass


class ActionExec:
    def __init__(self, sql: str, args: Optional[Iterable[Any]] = None) -> None:
        self.__sql = sql
        self.__args = args if args is not None else []
        pass

    async def __call__(self, cursor: Union[aiomysql.SSDictCursor, aiosqlite.Cursor]) -> int:
        sql = SqlConv(cursor)(self.__sql)
        await cursor.execute(sql, self.__args)
        return cursor.rowcount
    pass


class ActionIter:
    def __init__(self, sql: str, args: Optional[Iterable[Any]] = None) -> None:
        self.__sql = sql
        self.__args = args if args is not None else []
        pass

    async def __call__(self, cursor: Union[aiomysql.SSDictCursor, aiosqlite.Cursor]) -> AsyncGenerator[dict, None]:
        sql = SqlConv(cursor)(self.__sql)
        await cursor.execute(sql, self.__args)
        while (row := await cursor.fetchone()) is not None:
            yield dict(row)
            pass
        pass
    pass


class ConnExecutor:
    def __init__(self, conn: Union[aiomysql.Connection, aiosqlite.Connection]) -> None:
        self.__conn = conn
        self.__sql_type = 'mysql' if isinstance(conn, aiomysql.Connection) else 'sqlite'
        pass

    @property
    def sql_type(self) -> str:
        return self.__sql_type

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

    async def row_one(self, gen: ActionIter) -> Optional[dict]:
        res_row = None
        i = 0
        async with self.__conn.cursor() as cursor:
            async for row in gen(cursor):
                i += 1
                if i > 1:
                    raise MultipleResultsFound('期望一行，却返回多行数据')
                res_row = row
                pass
            return res_row
    pass


class ActionNorm:
    @staticmethod
    def table_exist(table_name: str) -> ActionIter:
        sql = """
SELECT COUNT(1) as COUNT FROM sqlite_master WHERE type='table' AND name=?;
"""
        return ActionIter(sql, (table_name,))
    pass
