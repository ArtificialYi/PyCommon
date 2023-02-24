from ...src.repository.rds import ServiceDB
from ..mock.rds import MockConnection, MockCursor, MockDBPool
from ...src.tool.func_tool import PytestAsyncTimeout


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
    async def test_select(self):
        res = []
        cursor = MockCursor().mock_set_exec(res)
        conn = MockConnection().mock_set_cursor(cursor)
        pool = MockDBPool('').mock_set_conn(conn)

        service = ServiceDB(pool)
        assert await service.select('sql', 'args') == res
        pass
    pass
