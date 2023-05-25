import aiosqlite
from pytest_mock import MockerFixture

from ...src.dependency.db import db
from ..base import MockDelay


class MockCursor(MockDelay, aiosqlite.Cursor):
    @staticmethod
    def mock_init(mocker: MockerFixture):
        cursor = MockCursor()
        conn = MockConnection().mock_set_cursor(cursor)
        mocker.patch('aiosqlite.connect', return_value=conn)

        async def mock_get_by(tag: str, field: str):
            return {
                'sql_type': 'sqlite',
            }.get(field, '0')
        mocker.patch(f'{db.__name__}.get_value_by_tag_and_field', new=mock_get_by)
        return cursor

    def __init__(self):
        MockDelay.__init__(self)
        self.__fetch_all_res: list = []
        self.__rowcount = 1
        pass

    async def execute(self, *args, **kwds):
        await self.mock_asleep()
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

    async def fetchone(self):
        await self.mock_asleep()
        if self.__fetch_idx < len(self.__fetch_all_res):
            res = self.__fetch_all_res[self.__fetch_idx]
            self.__fetch_idx += 1
            return res
        self.__fetch_idx = 0
        return None

    async def __aenter__(self):
        await self.mock_asleep()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.mock_asleep()
        pass

    def close(self):
        pass
    pass


class MockConnection(MockDelay, aiosqlite.Connection):
    def __init__(self, *args, **kwds):
        MockDelay.__init__(self)
        self.__cursor = MockCursor()
        self.__row_factory = None
        pass

    @property
    def row_factory(self):
        return self.__row_factory

    @row_factory.setter
    def row_factory(self, row_factory):
        self.__row_factory = row_factory
        pass

    def mock_set_cursor(self, cursor: MockCursor):
        self.__cursor = cursor
        return self

    def cursor(self):
        return self.__cursor

    async def execute(self, *args) -> MockCursor:
        await self.mock_asleep()
        return self.__cursor

    async def __aenter__(self):
        await self.mock_asleep()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self.mock_asleep()
        pass

    def close(self):
        pass
    pass
