import aiomysql
from typing import AsyncGenerator
from contextlib import asynccontextmanager

from .base import ConnExecutor
from ..data.rds import RDSConfigData
from ...tool.map_tool import MapKey
from ...configuration.norm.log import LoggerLocal


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


@MapKey(RDSConfigData.to_key)
async def get_pool(data: RDSConfigData) -> aiomysql.Pool:  # pragma: no cover
    return await aiomysql.create_pool(**{
        'maxsize': data.max_conn,
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

    async def pool(self):
        return await get_pool(self.__data)

    @asynccontextmanager
    async def __call__(self, use_transaction: bool = False) -> AsyncGenerator[ConnExecutor, None]:
        async with get_conn(await self.pool(), use_transaction) as conn:
            yield ConnExecutor(conn)
        pass
    pass
