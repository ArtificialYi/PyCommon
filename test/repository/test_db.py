from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.repository.db import ConnExecutor, SqlManage


class TestSqlManage:
    @PytestAsyncTimeout(1)
    async def test(self):
        manage = SqlManage()
        async with manage(True) as exec:
            assert type(exec) == ConnExecutor
            pass
        pass
    pass
