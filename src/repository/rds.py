from pymysql.cursors import SSDictCursor, Cursor
from pymysql.connections import Connection
from ..tool.base import AsyncBase

from ...configuration.base.rds import ActionDB, DBPool


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
    1. conn + cursor + sql + args + action => res
    """
    def __init__(self, action_db: type[ActionDB]) -> None:
        self.__action_db = action_db
        pass

    def __opt(self, pool: DBPool, sql: str, args):
        """线程安全的DB操作
        """
        with (
            pool.get_conn() as conn,
            conn.cursor(SSDictCursor) as cursor,
        ):
            return self.__action_db(conn, cursor, sql, args)

    async def send(self, pool: DBPool, sql: str, args):
        """仅能在主线程中调用
        """
        return await AsyncBase.func2coro_exec(self.__opt, pool, sql, args)
    pass


class ServiceDB:
    """对线程池做业务操作
    """
    def __init__(self, pool: DBPool) -> None:
        self.__pool = pool
        pass

    async def create(self, sql: str, args):
        return await OptDBSafe(ActionForceCommit).send(self.__pool, sql, args)

    async def update(self, sql: str, args):
        return await OptDBSafe(ActionAffectedMore).send(self.__pool, sql, args)

    async def select(self, sql: str, args):
        return await OptDBSafe(ActionNoTranslation).send(self.__pool, sql, args)
    pass
