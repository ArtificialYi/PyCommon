from pytest_mock import MockerFixture

from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout

from ...mock.db.sqlite import MockConnection, MockCursor

from ...src.repository.sqlite import ActionExec, ActionIter, SqliteManage


class TestSqliteManage:
    @PytestAsyncTimeout(1)
    async def test(self, mocker: MockerFixture):
        cursor = MockCursor()
        conn = MockConnection().mock_set_cursor(cursor)
        mocker.patch('aiosqlite.connect', return_value=conn)

        sqlite_manage = SqliteManage('test_local.db')

        # 无事务+iter
        async with sqlite_manage() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            i = 0
            async for _ in exec.iter(ActionIter('sql')):
                i += 1
                pass
            assert i == 3
            pass

        # 事务开启+exec
        async with sqlite_manage(True) as exec:
            # 正常提交事务
            assert await exec.exec(ActionExec('sql')) == 1
            pass

        # 抛出异常
        assert await FuncTool.is_async_err(self.__raise_exception, sqlite_manage)
        pass

    async def __raise_exception(self, sqlite_manage: SqliteManage):
        async with sqlite_manage(True):
            raise Exception('异常测试')
    pass
