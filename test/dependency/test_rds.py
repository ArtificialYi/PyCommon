import pytest

from ..timeout import PytestAsyncTimeout

from ...mock.func import MockException
from ...mock.db.rds import MockCursor
from ...mock.db_sync.rds import MockCursorSync
from ...src.exception.db import MultipleResultsFound
from ...src.dependency.db.rds import MysqlManage
from ...src.dependency.db.base import ActionExec, ActionIter
from ...src.dependency.db_sync.rds import MysqlManageSync
from ...src.dependency.db_sync.base import ActionExecSync, ActionIterSync


class TestMysqlManage:
    @PytestAsyncTimeout(1)
    async def test_err(self, mysql_cursor: tuple[MockCursor, MysqlManage]):
        _, sql_manage = mysql_cursor

        # 抛出异常
        with pytest.raises(MockException):
            async with sql_manage(True):
                raise MockException('异常测试')
        pass

    @PytestAsyncTimeout(1)
    async def test_iter(self, mysql_cursor: tuple[MockCursor, MysqlManage]):
        # 获取一个mysql管理器
        cursor, sql_manage = mysql_cursor

        # 无事务+iter
        async with sql_manage() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            sql_res = [1, 2, 3]
            i = 0
            async for row in exec.iter(ActionIter('sql')):
                assert row['id'] == sql_res[i]
                i += 1
                pass
            assert i == len(sql_res)
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_exec(self, mysql_cursor: tuple[MockCursor, MysqlManage]):
        # 获取一个mysql管理器
        _, sql_manage = mysql_cursor

        # 事务开启+exec
        async with sql_manage(True) as exec:
            # 正常提交事务
            assert await exec.exec(ActionExec('sql')) == 1
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_one(self, mysql_cursor: tuple[MockCursor, MysqlManage]):
        # 获取一个mysql管理器
        cursor, sql_manage = mysql_cursor

        # 无事务+iter
        async with sql_manage() as exec:
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
    pass


class TestMysqlManageSync:
    def test_err(self, mysql_cursor_sync: tuple[MockCursorSync, MysqlManageSync]):
        _, sql_manage = mysql_cursor_sync
        # 抛出异常
        with (
            pytest.raises(MockException),
            sql_manage(True)
        ):
            raise MockException('异常测试')

        pass

    def test_iter(self, mysql_cursor_sync: tuple[MockCursorSync, MysqlManageSync]):
        cursor, sql_manage = mysql_cursor_sync

        # 无事务+iter
        with sql_manage() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            sql_res = [1, 2, 3]
            i = 0
            for row in exec.iter(ActionIterSync('sql')):
                assert row['id'] == sql_res[i]
                i += 1
                pass
            assert i == len(sql_res)
            pass
        pass

    def test_exec(self, mysql_cursor_sync: tuple[MockCursorSync, MysqlManageSync]):
        _, sql_manage = mysql_cursor_sync

        # 事务开启+exec
        with sql_manage(True) as exec:
            # 正常提交事务
            assert exec.exec(ActionExecSync('sql')) == 1
            pass
        pass

    def test_one(self, mysql_cursor_sync: tuple[MockCursorSync, MysqlManageSync]):
        cursor, sql_manage = mysql_cursor_sync

        # 无事务+row_one
        with sql_manage() as exec:
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
