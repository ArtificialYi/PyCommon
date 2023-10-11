import pytest
from pytest_mock import MockerFixture

from ..mock.log import MockLogger, MockLoggerSync
from ..mock.db.rds import MockCursor as MockCursorRDS
from ..mock.db.sqlite import MockCursor as MockCursorSqlite
from ..mock.db_sync.rds import MockCursorSync as MockCursorRDSSync
from ..src.dependency.db.rds import MysqlManage
from ..src.dependency.db.manage import SqlManage


@pytest.fixture(scope='function', autouse=True)
def logger_pre(mocker: MockerFixture):
    MockLogger.mock_init(mocker)
    MockLoggerSync.mock_init(mocker)
    return mocker


@pytest.fixture(scope='function')
async def mysql_cursor(mocker: MockerFixture) -> tuple[MockCursorRDS, MysqlManage]:
    cursor = MockCursorRDS.mock_init(mocker)
    sql_manage = await SqlManage.get_instance_by_tag('test')
    return cursor, sql_manage


@pytest.fixture(scope='function')
def mysql_init_cursor_sync(mocker: MockerFixture) -> MockCursorRDSSync:
    return MockCursorRDSSync.mock_init(mocker)


@pytest.fixture(scope='function')
def sqlite_init_cursor(mocker: MockerFixture) -> MockCursorSqlite:
    return MockCursorSqlite.mock_init(mocker)
