from pymysql import Connection
from pytest_mock import MockerFixture
from pymysql.cursors import SSDictCursor
from pymysqlpool import ConnectionPool

from ...src.dependency.db_sync import manage, rds
from ..base import MockDelay


class MockCursorSync(MockDelay, SSDictCursor):
    """模拟cursor
    外部调用
    1. execute

    with调用
    1. close
    """
    @staticmethod
    def mock_init(mocker: MockerFixture):
        cursor = MockCursorSync()

        def tmp(*args):
            return MockDBPool('test').mock_set_conn(MockConnection().mock_set_cursor(cursor))
        mocker.patch(f'{rds.__name__}.get_pool', new=tmp)

        def mock_get_by(tag: str, field: str):
            return {
                'sql_type': 'mysql',
            }.get(field, '0')
        mocker.patch(f'{manage.__name__}.get_value_by_tag_and_field', new=mock_get_by)
        return cursor

    def __init__(self, *args):
        MockDelay.__init__(self)
        self.__fetch_all_res: list = []
        self.__fetch_idx = 0
        self.__rowcount = 1
        pass

    @property
    def rowcount(self):
        return self.__rowcount

    def mock_set_rowcount(self, rowcount: int):
        self.__rowcount = rowcount
        return self

    def mock_set_fetch_all(self, fetch_all_res: list):
        self.__fetch_all_res = fetch_all_res
        self.__fetch_idx = 0
        return self

    def execute(self, query, args=None):
        self.mock_sleep()
        return self

    def fetchone(self):
        self.mock_sleep()
        if self.__fetch_idx < len(self.__fetch_all_res):
            res = self.__fetch_all_res[self.__fetch_idx]
            self.__fetch_idx += 1
            return res
        self.__fetch_idx = 0
        return None

    def close(self):
        pass

    __del__ = close
    pass


class MockConnection(MockDelay, Connection):
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
        self.__cursor = MockCursorSync(self)
        pass

    def begin(self):
        self.mock_sleep()

    def rollback(self):
        self.mock_sleep()

    def commit(self):
        self.mock_sleep()

    def mock_set_cursor(self, cursor: MockCursorSync):
        self.__cursor = cursor
        return self

    def cursor(self, cursor=None):
        return self.__cursor

    def close(self):
        self.mock_sleep()
        pass

    def __enter__(self):
        return self

    def __exit__(self, *exc_info: object) -> None:
        return self.close()

    __del__ = close
    pass


class MockDBPool(MockDelay, ConnectionPool):
    """模拟DBPool
    外部调用
    1. get_conn
    """
    def __init__(self, flag: str) -> None:
        self.__db_name = flag
        MockDelay.__init__(self)
        self.__conn = MockConnection()
        pass

    @property
    def db_name(self):
        return self.__db_name

    def mock_set_conn(self, conn: MockConnection):
        self.__conn = conn
        return self

    def get_connection(self, *args, **kwds):
        return self.__conn
    pass
