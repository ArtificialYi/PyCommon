import sqlite3
import pytest

from ...src.dependency.db_sync.base import ActionExecSync, ActionIterSync

from ...src.dependency.db_sync.sqlite import SqliteManageSync

from ..timeout import PytestAsyncTimeout

from ...mock.func import MockException
from ...mock.db.sqlite import MockCursor, MockDB
from ...src.exception.db import MultipleResultsFound
from ...mock.db_sync.sqlite import MockCursorSync
from ...src.dependency.db.base import ActionExec, ActionIter
from ...src.dependency.db.sqlite import ServiceNorm, SqliteManage


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

    @PytestAsyncTimeout(1)
    async def test_one(self, sqlite_cursor: tuple[MockCursor, SqliteManage]):
        cursor, sql_mange = sqlite_cursor

        # 无事务+iter
        async with sql_mange() as exec:
            # 一行数据
            cursor.mock_set_fetch_all([{'id': 1}])
            row = await exec.row_one(ActionIter('sql'))
            assert row['id'] == 1

            # 无数据
            cursor.mock_set_fetch_all([])
            row = await exec.row_one(ActionIter('sql'))
            assert row is None

            # 多行数据
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}])
            with pytest.raises(MultipleResultsFound):
                await exec.row_one(ActionIter('sql'))
                pass
            pass
        pass

    async def __sql_exec(self, sql_manage: MockDB, action: ActionExec):
        async with sql_manage(True) as conn:
            return await conn.exec(action)
        pass

    @PytestAsyncTimeout(1)
    async def test_db_create(self):
        with MockDB('test.db') as sql_manage:
            assert isinstance(sql_manage, MockDB)
            assert not await ServiceNorm.table_exist(sql_manage, 'test')
            pass

        with pytest.raises(AttributeError):
            await ServiceNorm.table_exist(sql_manage, 'test')
        pass

    @pytest.fixture
    def db_create(self):
        with MockDB('test.db') as sql_manage:
            yield sql_manage
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_table_create(self, db_create: MockDB):
        table_name = 'test_table'
        sql = f"""
CREATE TABLE "main"."{table_name}" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT
);
        """
        action = ActionExec(sql)

        assert not await ServiceNorm.table_exist(db_create, table_name)
        assert await self.__sql_exec(db_create, action) == -1
        assert await ServiceNorm.table_exist(db_create, table_name)

        with pytest.raises(sqlite3.OperationalError):
            assert await self.__sql_exec(db_create, action) == -1
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_sql_type(self, db_create: MockDB):
        async with db_create() as conn:
            assert conn.sql_type == 'sqlite'
            pass
        pass
    pass


class TestSqliteManageSync:
    def test_err(self, sqlite_cursor_sync: tuple[MockCursorSync, SqliteManageSync]):
        _, sql_mange = sqlite_cursor_sync

        # 抛出异常
        with pytest.raises(MockException):
            with sql_mange(True):
                raise MockException('异常测试')
        pass

    def test_iter(self, sqlite_cursor_sync: tuple[MockCursorSync, SqliteManageSync]):
        cursor, sql_mange = sqlite_cursor_sync

        # 无事务+iter
        with sql_mange() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            i = 0
            for _ in exec.iter(ActionIterSync('sql')):
                i += 1
                pass
            assert i == 3
            pass
        pass

    def test_exec(self, sqlite_cursor_sync: tuple[MockCursorSync, SqliteManageSync]):
        _, sql_mange = sqlite_cursor_sync

        # 事务开启+exec
        with sql_mange(True) as exec:
            # 正常提交事务
            assert exec.exec(ActionExecSync('sql')) == 1
            pass
        pass

    def test_one(self, sqlite_cursor_sync: tuple[MockCursorSync, SqliteManageSync]):
        cursor, sql_mange = sqlite_cursor_sync

        # 无事务+iter
        with sql_mange() as exec:
            # 一行数据
            cursor.mock_set_fetch_all([{'id': 1}])
            row = exec.row_one(ActionIterSync('sql'))
            assert row['id'] == 1

            # 无数据
            cursor.mock_set_fetch_all([])
            row = exec.row_one(ActionIterSync('sql'))
            assert row is None

            # 多行数据
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}])
            with pytest.raises(MultipleResultsFound):
                exec.row_one(ActionIterSync('sql'))
                pass
            pass
        pass
    pass
