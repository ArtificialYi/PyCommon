from contextlib import asynccontextmanager
import aiomysql
from pytest_mock import MockerFixture

from ..base import MockDelay
from ...src.repository import rds


class MockCursor(MockDelay, aiomysql.SSDictCursor):
    """模拟cursor
    外部调用
    1. execute

    with调用
    1. close
    """
    def __init__(self, *args):
        MockDelay.__init__(self)
        self.__exec_res = None
        self.__fetch_all_res: list = None  # type: ignore
        self.__fetch_idx = 0
        self.__rowcount = 1
        pass

    @property
    def rowcount(self):
        return self.__rowcount

    def mock_set_exec(self, exec_res: int):
        self.__exec_res = exec_res
        return self

    def mock_set_rowcount(self, rowcount: int):
        self.__rowcount = rowcount
        return self

    def mock_set_fetch_all(self, fetch_all_res):
        self.__fetch_all_res = fetch_all_res
        self.__fetch_idx = 0
        return self

    async def execute(self, query, args=None):
        self.mock_sleep()
        return self.__exec_res

    async def fetchone(self):
        await self.mock_asleep()
        if self.__fetch_idx < len(self.__fetch_all_res):
            res = self.__fetch_all_res[self.__fetch_idx]
            self.__fetch_idx += 1
            return res
        self.__fetch_idx = 0
        return None

    def close(self):
        pass

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        pass

    __del__ = close
    pass


class MockConnection(MockDelay, aiomysql.Connection):
    """模拟conn
    外部调用
    1. begin
    2. rollback
    3. commit
    4. cursor

    with调用
    1. close
    """
    def __init__(self, *args, **kwds):
        MockDelay.__init__(self)
        self.__cursor = MockCursor(self)
        pass

    async def begin(self):
        await self.mock_asleep()

    async def rollback(self):
        await self.mock_asleep()

    async def commit(self):
        await self.mock_asleep()

    def mock_set_cursor(self, cursor: MockCursor):
        self.__cursor = cursor
        return self

    def cursor(self, cursor=None):
        return self.__cursor

    def close(self):
        self.mock_sleep()
        pass

    async def ensure_closed(self):
        await self.mock_asleep()
        pass

    __del__ = close
    pass


class MockDBPool(MockDelay, aiomysql.Pool):
    @staticmethod
    def mocker(mocker: MockerFixture) -> MockCursor:
        cursor = MockCursor()

        async def tmp(*args):
            return MockDBPool('test').mock_set_conn(MockConnection().mock_set_cursor(cursor))
        mocker.patch(f'{rds.__name__}.get_pool', new=tmp)
        return cursor

    """模拟DBPool
    外部调用
    1. get_conn
    """
    def __init__(self, flag: str) -> None:
        self.__db_name = flag
        MockDelay.__init__(self)
        self.__conn = MockConnection()
        pass

    async def __await__(self):
        yield self

    @property
    def db_name(self):
        return self.__db_name

    def mock_set_conn(self, conn: MockConnection):
        self.__conn = conn
        return self

    @asynccontextmanager
    async def acquire(self):
        await self.mock_asleep()
        yield self.__conn
        await self.mock_asleep()
        pass
    pass
