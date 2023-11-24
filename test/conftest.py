import pytest
from pytest_mock import MockerFixture

from ..src.dependency.db_sync.sqlite import SqliteManageSync

from ..src.dependency.db.sqlite import SqliteManage

from ..mock.log import MockLogger, MockLoggerSync
from ..mock.db.rds import MockCursor as MockCursorRDS
from ..mock.db.sqlite import MockCursor as MockCursorSqlite
from ..mock.db_sync.rds import MockCursorSync as MockCursorRDSSync
from ..mock.db_sync.sqlite import MockCursorSync as MockCursorSqliteSync
from ..src.dependency.db.rds import MysqlManage
from ..src.dependency.db.manage import SqlManage
from ..src.dependency.db_sync.rds import MysqlManageSync
from ..src.dependency.db_sync.manage import SqlManageSync


@pytest.fixture(scope='function', autouse=True)
def logger_pre(mocker: MockerFixture):
    MockLogger.mock_init(mocker)
    MockLoggerSync.mock_init(mocker)
    return mocker


@pytest.fixture(scope='function', autouse=True)
def config_pre(mocker: MockerFixture):
    pass


@pytest.fixture(scope='function')
async def mysql_cursor(mocker: MockerFixture) -> tuple[MockCursorRDS, MysqlManage]:
    cursor = MockCursorRDS.mock_init(mocker)
    sql_manage = await SqlManage.get_instance_by_tag('test')
    return cursor, sql_manage


@pytest.fixture(scope='function')
def mysql_cursor_sync(mocker: MockerFixture) -> tuple[MockCursorRDSSync, MysqlManageSync]:
    cursor = MockCursorRDSSync.mock_init(mocker)
    sql_manage = SqlManageSync.get_instance_by_tag('test')
    return cursor, sql_manage


@pytest.fixture(scope='function')
async def sqlite_cursor(mocker: MockerFixture) -> tuple[MockCursorSqlite, SqliteManage]:
    cursor = MockCursorSqlite.mock_init(mocker)
    sql_manage = await SqlManage.get_instance_by_tag('test')
    return cursor, sql_manage


@pytest.fixture(scope='function')
def sqlite_cursor_sync(mocker: MockerFixture) -> tuple[MockCursorSqliteSync, SqliteManageSync]:
    cursor = MockCursorSqliteSync.mock_init(mocker)
    sql_manage = SqlManageSync.get_instance_by_tag('test')
    return cursor, sql_manage
