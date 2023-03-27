from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.repository.rds import ActionExec, ActionIter, MysqlManage
from ...mock.db.rds import MockConnection, MockCursor, MockDBPool
from pytest_mock import MockerFixture


class TestMysqlManage:
    @PytestAsyncTimeout(1)
    async def test(self, mocker: MockerFixture):
        # 获取一个mysql管理器
        cursor = MockCursor()
        pool = MockDBPool('test').mock_set_conn(MockConnection().mock_set_cursor(cursor))
        mocker.patch('PyCommon.src.repository.rds.pool_manage', return_value=pool)
        mysql_manage = await MysqlManage('test')

        # 无事务+iter
        async with mysql_manage() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            sql_res = [1, 2, 3]
            i = 0
            async for _ in exec.iter(ActionIter('sql')):
                i += 1
                pass
            assert i == len(sql_res)
            pass

        # 事务开启+exec
        async with mysql_manage(True) as exec:
            # 正常提交事务
            assert await exec.exec(ActionExec('sql')) is None
            pass

        # 抛出异常
        async with mysql_manage(True) as exec:
            raise Exception('这个异常会被吞掉，代码里需要留下日志')
        pass
    pass
