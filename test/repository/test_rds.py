from ...mock.rds import MockConnection, MockCursor, MockDBPool
from ...src.repository.rds import ServiceDB
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout


class TestServiceDB:
    @PytestAsyncTimeout(1)
    async def test_create(self):
        res = 0
        cursor = MockCursor().mock_set_exec(res)
        conn = MockConnection().mock_set_cursor(cursor)
        pool = MockDBPool('').mock_set_conn(conn)

        service = ServiceDB(pool)
        assert await service.create('sql', 'args') == res
        pass

    @PytestAsyncTimeout(1)
    async def test_update(self):
        res = 1
        cursor = MockCursor().mock_set_exec(res)
        conn = MockConnection().mock_set_cursor(cursor)
        pool = MockDBPool('').mock_set_conn(conn)

        service = ServiceDB(pool)
        assert await service.update('sql', 'args') == res
        pass

    @PytestAsyncTimeout(1)
    async def test_update_err(self):
        res = -1
        cursor = MockCursor().mock_set_exec(res)
        conn = MockConnection().mock_set_cursor(cursor)
        pool = MockDBPool('').mock_set_conn(conn)

        service = ServiceDB(pool)
        assert await FuncTool.is_async_err(service.update, 'sql', 'args')
        pass

    @PytestAsyncTimeout(1)
    async def test_select(self):
        res_exec = 0
        res_fetch = []
        cursor = MockCursor().mock_set_exec(res_exec).mock_set_fetch_all(res_fetch)
        conn = MockConnection().mock_set_cursor(cursor)
        pool = MockDBPool('').mock_set_conn(conn)

        service = ServiceDB(pool)
        assert await service.select('sql', 'args') == res_fetch
        pass
    pass
