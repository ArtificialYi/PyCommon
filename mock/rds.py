from time import sleep
from ..configuration.rds import DBPool
from pymysql.cursors import SSDictCursor
from pymysql.connections import Connection


class MockDelay:
    def __init__(self, delay: float = 0.01) -> None:
        self.__delay = delay
        pass

    def mock_sleep(self, delay=None):
        sleep(self.__delay if delay is None else delay)
        pass

    def mock_set_delay(self, delay: float):
        self.__delay = delay
        pass
    pass


class MockCursor(MockDelay, SSDictCursor):
    """模拟cursor
    外部调用
    1. execute

    with调用
    1. close
    """
    def __init__(self, *args):
        MockDelay.__init__(self)
        self.__exec_res = None
        self.__fetch_all_res = None
        pass

    def mock_set_exec(self, exec_res: int):
        self.__exec_res = exec_res
        return self

    def mock_set_fetch_all(self, fetch_all_res):
        self.__fetch_all_res = fetch_all_res
        return self

    def execute(self, query, args=None):
        self.mock_sleep()
        return self.__exec_res

    def fetchall(self):
        self.mock_sleep()
        return self.__fetch_all_res

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
        self.__cursor = MockCursor(self)
        pass

    def begin(self):
        self.mock_sleep()

    def rollback(self):
        self.mock_sleep()

    def commit(self):
        self.mock_sleep()

    def mock_set_cursor(self, cursor: MockCursor):
        self.__cursor = cursor
        return self

    def cursor(self, cursor=None):
        self.mock_sleep()
        return self.__cursor

    def close(self):
        self.mock_sleep()
        pass
    pass


class MockDBPool(MockDelay, DBPool):
    """模拟DBPool
    外部调用
    1. get_conn
    """
    def __init__(self, db_name: str) -> None:
        self.__db_name = db_name
        MockDelay.__init__(self)
        self.__conn = MockConnection()
        pass

    @property
    def db_name(self):
        return self.__db_name

    def mock_set_conn(self, conn: MockConnection):
        self.__conn = conn
        return self

    def get_conn(self) -> Connection:
        self.mock_sleep()
        return self.__conn
    pass
