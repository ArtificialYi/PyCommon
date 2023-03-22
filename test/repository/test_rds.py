from ...configuration.rds import NormAction
from ...src.repository.rds import DBExecutorSafe, FetchAction
from ...mock.rds import MockConnection, MockCursor, MockDBPool
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout


class TestDBExecutor:
    @PytestAsyncTimeout(1)
    async def test_fail(self):
        # 不开启asyn with无法使用
        cursor = MockCursor()
        db = DBExecutorSafe(MockDBPool('test').mock_set_conn(MockConnection().mock_set_cursor(cursor)))
        assert await FuncTool.is_async_err(db.execute, NormAction())
        assert await FuncTool.is_async_err(db.iter_opt, FetchAction('sql'))

        # 无事务+iter
        async with db:
            cursor.mock_set_fetch_all([1, 2, 3])
            i = 0
            async for _ in db.iter_opt(FetchAction('sql')):
                i += 1
                pass
            assert i == 3
            pass
        pass
    pass
