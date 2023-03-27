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
