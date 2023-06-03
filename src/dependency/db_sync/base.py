from typing import Any, Generator, Optional, Union
import pymysql
from pymysql.cursors import SSDictCursor
import sqlite3

from ...tool.sql_tool import Mysql2Other


class ActionExecSync:
    def __init__(self, sql: str, args: Optional[tuple | dict] = None) -> None:
        self.__sql = sql
        self.__args = args if args is not None else []
        pass

    def __call__(self, cursor: Union[SSDictCursor, sqlite3.Cursor]) -> int:
        sql = self.__sql if isinstance(cursor, SSDictCursor) else Mysql2Other.sqlite(self.__sql)
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
    ) -> Generator[dict[str, Any], SSDictCursor | sqlite3.Cursor, None]:
        sql = self.__sql if isinstance(cursor, SSDictCursor) else Mysql2Other.sqlite(self.__sql)
        cursor.execute(sql, self.__args)
        while (row := cursor.fetchone()) is not None:
            yield dict(row)
            pass
        pass
    pass


class ConnExecutorSync:
    def __init__(self, conn: pymysql.Connection | sqlite3.Connection) -> None:
        self.__conn = conn
        pass

    def exec(self, coro: ActionExecSync) -> int:
        cursor = self.__conn.cursor()
        res = coro(cursor)
        cursor.close()
        return res

    def iter(self, gen: ActionIterSync) -> Generator[dict, ActionIterSync, None]:
        cursor = self.__conn.cursor()
        for row in gen(cursor):
            yield row
            pass
        cursor.close()
        pass
    pass
