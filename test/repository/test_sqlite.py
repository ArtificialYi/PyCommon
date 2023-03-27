from pytest_mock import MockerFixture

from ...mock.db.sqlite import MockConnection, MockCursor

from ...src.repository.sqlite import ActionExec, ActionIter, SqliteManage


class TestSqliteManage:
    async def test(self, mocker: MockerFixture):
        cursor = MockCursor()
        conn = MockConnection().mock_set_cursor(cursor)
        mocker.patch('aiosqlite.connect', return_value=conn)

        manage = SqliteManage('test_local.db')

        # 无事务+iter
        async with manage() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            i = 0
            async for _ in exec.iter(ActionIter('sql')):
                i += 1
                pass
            assert i == 3
            pass

        # 事务开启+exec
        async with manage(True) as exec:
            # 正常提交事务
            assert await exec.exec(ActionExec('sql')) == 1
            pass

        # 抛出异常
        async with manage(True) as exec:
            raise Exception('这个异常会被吞掉，代码里需要留下日志')
        pass
    pass
