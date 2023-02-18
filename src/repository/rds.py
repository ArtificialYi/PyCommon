from abc import abstractmethod
from typing import Dict, Tuple
from pymysql.cursors import SSDictCursor, Cursor
from pymysql.connections import Connection
from ..tool.base import AsyncBase

from ...configuration.base.rds import DBPool


class ActionDB:
    @abstractmethod
    def __new__(cls, conn: Connection, cursor: Cursor, sql: str, args):
        pass
    pass


class ActionAffectedMore(ActionDB):
    def __new__(cls, conn: Connection, cursor: Cursor, sql: str, args):
        conn.begin()
        effected_rows = cursor.execute(sql, args)
        if not isinstance(effected_rows, int):
            conn.rollback()
            raise Exception(f'异常SQL调用:{sql}')
        conn.commit()
        return effected_rows
    pass


class ActionForceCommit(ActionDB):
    def __new__(cls, conn: Connection, cursor: Cursor, sql: str, args):
        conn.begin()
        effected_rows = cursor.execute(sql, args)
        conn.commit()
        return effected_rows
    pass


class ActionNoTranslation(ActionDB):
    def __new__(cls, conn: Connection, cursor: Cursor, sql: str, args):
        return cursor.execute(sql, args)
    pass


class OptDBSafe:
    """使用固定的DB的业务逻辑调用不同的Action
    线程安全
    1. conn + cursor + sql + args + action => res
    """
    def __init__(self, action_db: type[ActionDB]) -> None:
        self.__action_db = action_db
        pass

    def opt(self, pool: DBPool, sql: str, args):
        with (
            pool.get_conn() as conn,
            conn.cursor(SSDictCursor) as cursor,
        ):
            return self.__action_db(conn, cursor, sql, args)
    pass


class PoolMap:
    """连接池管理类
    仅在主线程中使用
    """
    __POOL_MAP: Dict[str, DBPool] = dict()

    @classmethod
    def get_pool(cls, db_name: str):
        """获取线程池
        """
        if cls.__POOL_MAP.get(db_name, None) is not None:
            return cls.__POOL_MAP[db_name]

        cls.__POOL_MAP[db_name] = DBPool(db_name)
        return cls.__POOL_MAP[db_name]
    pass


class PoolOptDB:
    """往线程池中发送请求
    仅可在主线程中被调用
    """
    def __init__(self, db_name: str, action: type[ActionDB]) -> None:
        self.__pool = PoolMap.get_pool(db_name)
        self.__opt = OptDBSafe(action)
        pass

    async def send(self, sql: str, args):
        return await AsyncBase.func2coro_exec(self.__opt.opt, self.__pool, sql, args)
    pass


class PoolOptMap:
    """线程池操作管理类
    """
    __OPT_MAP: Dict[Tuple[str, type[ActionDB]], PoolOptDB] = dict()

    @classmethod
    def get_pool_opt(cls, db_name: str, action: type[ActionDB]):
        key = (db_name, action)
        if cls.__OPT_MAP.get(key, None) is not None:
            return cls.__OPT_MAP[key]

        cls.__OPT_MAP[key] = PoolOptDB(*key)
        return cls.__OPT_MAP[key]
    pass


class ServiceDB:
    def __init__(self, db_name: str) -> None:
        self.__db_name = db_name
        pass

    async def create(self, sql: str, args):
        pool_opt = PoolOptMap.get_pool_opt(self.__db_name, ActionForceCommit)
        return await pool_opt.send(sql, args)

    async def update(self, sql: str, args):
        pool_opt = PoolOptMap.get_pool_opt(self.__db_name, ActionAffectedMore)
        return await pool_opt.send(sql, args)

    async def select(self, sql: str, args):
        pool_opt = PoolOptMap.get_pool_opt(self.__db_name, ActionNoTranslation)
        return await pool_opt.send(sql, args)
    pass
