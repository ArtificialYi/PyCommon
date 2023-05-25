import pytest
from pytest_mock import MockerFixture

from ...src.dependency.db.db import SqlManage
from ...src.dependency.db.base import ActionExec, ActionIter
from ...mock.func import MockException
from ...src.tool.func_tool import PytestAsyncTimeout
from ...mock.db.sqlite import MockCursor


class TestSqliteManage:
    @PytestAsyncTimeout(1)
    async def test(self, mocker: MockerFixture):
        cursor = MockCursor.mock_init(mocker)
        sqlite_manage = await SqlManage.get_instance_by_tag('test')

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
        with pytest.raises(MockException):
            await self.__raise_exception(sqlite_manage)
        pass

    async def __raise_exception(self, sqlite_manage):
        async with sqlite_manage(True):
            raise MockException('异常测试')
    pass
