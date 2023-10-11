import pytest

from ..timeout import PytestAsyncTimeout

from ...mock.func import MockException
from ...mock.db.sqlite import MockCursor
from ...src.dependency.db.base import ActionExec, ActionIter
from ...src.dependency.db.sqlite import SqliteManage


class TestSqliteManage:
    @PytestAsyncTimeout(1)
    async def test_err(self, sqlite_cursor: tuple[MockCursor, SqliteManage]):
        _, sql_mange = sqlite_cursor

        # 抛出异常
        with pytest.raises(MockException):
            async with sql_mange(True):
                raise MockException('异常测试')
        pass

    @PytestAsyncTimeout(1)
    async def test_iter(self, sqlite_cursor: tuple[MockCursor, SqliteManage]):
        cursor, sql_mange = sqlite_cursor

        # 无事务+iter
        async with sql_mange() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            i = 0
            async for _ in exec.iter(ActionIter('sql')):
                i += 1
                pass
            assert i == 3
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_exec(self, sqlite_cursor: tuple[MockCursor, SqliteManage]):
        _, sql_mange = sqlite_cursor

        # 事务开启+exec
        async with sql_mange(True) as exec:
            # 正常提交事务
            assert await exec.exec(ActionExec('sql')) == 1
            pass
        pass
    pass
