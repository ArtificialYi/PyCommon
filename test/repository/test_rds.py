from ...configuration.rds import NormAction
from ...src.repository.rds import DBExecutorSafe, ExecuteAction, FetchAction
from ...mock.rds import MockConnection, MockCursor, MockDBPool
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout


class TestDBExecutor:
    @PytestAsyncTimeout(1)
    async def test_fail(self):
        # 不开启asyn with无法使用
        cursor = MockCursor()
        pool = MockDBPool('test').mock_set_conn(MockConnection().mock_set_cursor(cursor))
        db = DBExecutorSafe(pool)
        assert await FuncTool.is_async_err(db.execute, NormAction())
        assert await FuncTool.is_async_gen_err(db.iter_opt(FetchAction('sql')))

        # 无事务+iter
        async with db:
            sql_res = [1, 2, 3]
            cursor.mock_set_fetch_all(sql_res)
            i = 0
            async for _ in db.iter_opt(FetchAction('sql')):
                i += 1
                pass
            assert i == len(sql_res)
            pass

        # 事务开启+exec
        db = DBExecutorSafe(pool, True)
        async with db:
            # 正常提交事务
            assert await db.execute(ExecuteAction('sql')) is None
            pass
        async with db:
            # 抛出异常
            raise Exception('这个异常会被吞掉，代码里需要留下日志')
        pass
    pass
