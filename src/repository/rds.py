from contextlib import asynccontextmanager
from typing import AsyncGenerator
import aiomysql

from ..tool.base import BaseTool
from ..tool.map_tool import MapKey
from .base import ConnExecutor
from ...configuration.log import LoggerLocal


# async def __rollback_unit(conn: aiomysql.Connection):
#     """执行SQL回滚
#     抛出非业务异常
#     """
#     try:
#         await conn.rollback()
#     except BaseException as e:
#         await LoggerLocal.exception(e, f'rollback失败:{type(e).__name__}|{e}')
#         ExceptTool.raise_not_exception(e)
#         pass
#     pass


@asynccontextmanager
async def __transaction(conn: aiomysql.Connection):
    """事务开启与关闭
    当遇到业务异常时，执行回滚
    """
    try:
        await conn.begin()
        yield
        await conn.commit()
    except BaseException as e:
        await LoggerLocal.exception(e, f'db_conn事务异常:{type(e).__name__}|{e}')
        await conn.rollback()
        raise
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


class RDSConfigData:
    FIELDS = ('host', 'port', 'user', 'password', 'db')

    def __init__(self, host: str, port: str, user: str, password: str, db: str) -> None:
        self.host = host
        self.port = int(port) if len(port) > 0 else 0
        self.user = user
        self.password = password
        self.db = db
        pass
    pass


@MapKey(BaseTool.return_self)
async def get_pool(data: RDSConfigData):  # pragma: no cover
    return await aiomysql.create_pool(**{
        'host': data.host,
        'port': data.port,
        'user': data.user,
        'password': data.password,
        'db': data.db,
        'cursorclass': aiomysql.SSDictCursor,
    })


class MysqlManage:
    def __init__(self, data: RDSConfigData) -> None:
        self.__data = data
        pass

    @asynccontextmanager
    async def __call__(self, use_transaction: bool = False) -> AsyncGenerator[ConnExecutor, None]:
        async with get_conn(await get_pool(self.__data), use_transaction) as conn:
            yield ConnExecutor(conn)
        pass
    pass
