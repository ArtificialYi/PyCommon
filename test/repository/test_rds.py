import pytest
from ...mock.func import MockException
from ...src.repository.db import ActionExec, ActionIter
from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.repository.rds import MysqlManage
from ...mock.db.rds import MockConnection, MockCursor, MockDBPool
from pytest_mock import MockerFixture


class TestMysqlManage:
    @PytestAsyncTimeout(1)
    async def test(self, mocker: MockerFixture):
        # 获取一个mysql管理器
        cursor = MockCursor()

        async def tmp(flag: str):
            return MockDBPool(flag).mock_set_conn(MockConnection().mock_set_cursor(cursor))
        mocker.patch('PyCommon.src.repository.rds.pool_manage', new=tmp)
        mysql_manage = MysqlManage('test')

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
            assert await exec.exec(ActionExec('sql')) == 1
            pass

        # 抛出异常
        with pytest.raises(MockException):
            await self.__raise_exception(mysql_manage)
        pass

    async def __raise_exception(self, manage: MysqlManage):
        async with manage(True):
            raise MockException('异常测试')
    pass
