from sqlite3 import Cursor, Connection
from pytest_mock import MockerFixture

from ..base import MockDelay

from ...src.dependency.db_sync import manage


class MockCursorSync(MockDelay, Cursor):
    @staticmethod
    def mock_init(mocker: MockerFixture):
        cursor = MockCursorSync()
        conn = MockConnectionSync().mock_set_cursor(cursor)
        mocker.patch('sqlite3.connect', return_value=conn)

        def mock_get_by(tag: str, field: str):
            return {
                'sql_type': 'sqlite',
            }.get(field, '0')
        mocker.patch(f'{manage.__name__}.get_value_by_tag_and_field', new=mock_get_by)
        return cursor

    def __init__(self, *args):
        MockDelay.__init__(self)
        self.__fetch_all_res: list = []
        self.__fetch_idx = 0
        self.__rowcount = 1
        pass

    def execute(self, *args, **kwds):
        self.mock_sleep()
        return self

    def mock_set_rowcount(self, rowcount: int):
        self.__rowcount = rowcount
        return self

    @property
    def rowcount(self):
        return self.__rowcount

    def mock_set_fetch_all(self, fetch_all_res: list):
        self.__fetch_all_res = fetch_all_res
        self.__fetch_idx = 0
        return self

    def fetchone(self):
        self.mock_sleep()
        if self.__fetch_idx < len(self.__fetch_all_res):
            res = self.__fetch_all_res[self.__fetch_idx]
            self.__fetch_idx += 1
            return res
        self.__fetch_idx = 0
        return None

    def __enter__(self):
        self.mock_sleep()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.mock_sleep()
        pass

    def close(self):
        pass
    pass


class MockConnectionSync(MockDelay, Connection):
    def __init__(self, *args, **kwds):
        MockDelay.__init__(self)
        self.__cursor = MockCursorSync()
        self.__row_factory = None
        pass

    @property
    def row_factory(self):
        return self.__row_factory

    @row_factory.setter
    def row_factory(self, row_factory):
        self.__row_factory = row_factory
        pass

    def mock_set_cursor(self, cursor: MockCursorSync):
        self.__cursor = cursor
        return self

    def cursor(self):
        return self.__cursor

    def execute(self, *args) -> MockCursorSync:
        self.mock_sleep()
        return self.__cursor

    def __enter__(self):
        self.mock_sleep()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        self.mock_sleep()
        pass

    def close(self):
        pass
    pass
