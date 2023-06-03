import pytest
from pytest_mock import MockerFixture

from ...src.dependency.db_sync.rds import MysqlManageSync

from ...src.dependency.db_sync.base import ActionExecSync, ActionIterSync

from ...src.dependency.db_sync.manage import SqlManageSync

from ...mock.db_sync.rds import MockCursorSync
from ..timeout import PytestAsyncTimeout
from ...src.dependency.db.manage import SqlManage
from ...src.dependency.db.base import ActionExec, ActionIter
from ...mock.func import MockException
from ...mock.db.rds import MockCursor


class TestMysqlManage:
    @PytestAsyncTimeout(1)
    async def test(self, mocker: MockerFixture):
        # 获取一个mysql管理器
        cursor = MockCursor.mock_init(mocker)
        mysql_manage = await SqlManage.get_instance_by_tag('test')

        # 无事务+iter
        async with mysql_manage() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            sql_res = [1, 2, 3]
            i = 0
            async for row in exec.iter(ActionIter('sql')):
                assert row['id'] == sql_res[i]
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


class TestMysqlManageSync:
    def test(self, mocker: MockerFixture):
        cursor = MockCursorSync.mock_init(mocker)
        mysql_manage_sync = SqlManageSync.get_instance_by_tag('test')

        # 无事务+iter
        with mysql_manage_sync() as exec:
            cursor.mock_set_fetch_all([{'id': 1}, {'id': 2}, {'id': 3}])
            sql_res = [1, 2, 3]
            i = 0
            for row in exec.iter(ActionIterSync('sql')):
                assert row['id'] == sql_res[i]
                i += 1
                pass
            assert i == len(sql_res)
            pass

        # 事务开启+exec
        with mysql_manage_sync(True) as exec:
            # 正常提交事务
            assert exec.exec(ActionExecSync('sql')) == 1
            pass

        # 抛出异常
        with pytest.raises(MockException):
            self.__raise_exception(mysql_manage_sync)
        pass

    def __raise_exception(self, manage: MysqlManageSync):
        with manage(True):
            raise MockException('异常测试')
    pass
