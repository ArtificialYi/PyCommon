from typing import Any, Generator, Optional, Union
import pymysql
from pymysql.cursors import SSDictCursor
import sqlite3

from ...exception.db import MultipleResultsFound

from ...tool.sql_tool import SQLTool


class SqlConv:
    def __init__(self, cursor: SSDictCursor | sqlite3.Cursor) -> None:
        self.__conv = SQLTool.to_mysql if isinstance(cursor, SSDictCursor) else SQLTool.to_sqlite
        pass

    def __call__(self, sql: str) -> str:
        return self.__conv(sql)
    pass


class ActionExecSync:
    def __init__(self, sql: str, args: Optional[tuple | dict] = None) -> None:
        self.__sql = sql
        self.__args = args if args is not None else []
        pass

    def __call__(self, cursor: Union[SSDictCursor, sqlite3.Cursor]) -> int:
        sql = SqlConv(cursor)(self.__sql)
        cursor.execute(sql, self.__args)
        return cursor.rowcount
    pass


class ActionIterSync:
    def __init__(self, sql: str, args: Optional[tuple | dict] = None) -> None:
        self.__sql = sql
        self.__args = args if args is not None else []
        pass

    def __call__(
        self, cursor: SSDictCursor | sqlite3.Cursor,
    ) -> Generator[dict[str, Any], None, None]:
        sql = SqlConv(cursor)(self.__sql)
        cursor.execute(sql, self.__args)
        while (row := cursor.fetchone()) is not None:
            yield dict(row)
            pass
        pass
    pass


class ConnExecutorSync:
    def __init__(self, conn: pymysql.Connection | sqlite3.Connection) -> None:
        self.__conn = conn
        self.__sql_type = 'mysql' if isinstance(conn, pymysql.Connection) else 'sqlite'
        pass

    @property
    def sql_type(self) -> str:
        return self.__sql_type

    def exec(self, sql: str, args: tuple) -> int:
        func = ActionExecSync(sql, args)
        cursor = self.__conn.cursor()
        res = func(cursor)
        cursor.close()
        return res

    def iter(self, sql: str, args: tuple) -> Generator[dict, None, None]:
        gen = ActionIterSync(sql, args)
        cursor = self.__conn.cursor()
        for row in gen(cursor):
            yield row
            pass
        cursor.close()
        pass

    def row_one(self, sql: str, args: tuple) -> Optional[dict]:
        gen = ActionIterSync(sql, args)
        res_row = None
        i = 0
        cursor = self.__conn.cursor()
        for row in gen(cursor):
            i += 1
            if i > 1:
                raise MultipleResultsFound('期望一行，却返回多行数据')
            res_row = row
            pass
        return res_row
    pass
