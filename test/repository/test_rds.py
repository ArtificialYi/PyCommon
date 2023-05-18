import pytest
from pytest_mock import MockerFixture

from ...src.repository.db import SqlManage
from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.repository.base import ActionExec, ActionIter
from ...mock.func import MockException
from ...mock.db.rds import MockCursor


class TestMysqlManage:
    @PytestAsyncTimeout(1)
    async def test(self, mocker: MockerFixture):
        # 获取一个mysql管理器
        cursor = MockCursor.create(mocker)
        mysql_manage = await SqlManage.get_instance_by_tag('test')

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

    async def __raise_exception(self, manage):
        async with manage(True):
            raise MockException('异常测试')
    pass
