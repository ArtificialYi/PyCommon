import pytest
from pytest_mock import MockerFixture


from ..mock.log import MockLogger, MockLoggerSync
from ..mock.db.rds import MockCursor as MockCursorRDS
from ..mock.db_sync.rds import MockCursorSync as MockCursorRDSSync
from ..mock.db.sqlite import MockCursor as MockCursorSqlite


@pytest.fixture(scope='function', autouse=True)
def logger_pre(mocker: MockerFixture):
    MockLogger.mock_init(mocker)
    MockLoggerSync.mock_init(mocker)
    return mocker


@pytest.fixture(scope='function')
def mysql_init_cursor(mocker: MockerFixture) -> MockCursorRDS:
    return MockCursorRDS.mock_init(mocker)


@pytest.fixture(scope='function')
def mysql_init_cursor_sync(mocker: MockerFixture) -> MockCursorRDSSync:
    return MockCursorRDSSync.mock_init(mocker)


@pytest.fixture(scope='function')
def sqlite_init_cursor(mocker: MockerFixture) -> MockCursorSqlite:
    return MockCursorSqlite.mock_init(mocker)
