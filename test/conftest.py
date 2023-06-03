import pytest
from pytest_mock import MockerFixture

from ..mock.log import MockLogger, MockLoggerSync


@pytest.fixture(autouse=True)
def logger_pre(mocker: MockerFixture):
    MockLogger.mock_init(mocker)
    MockLoggerSync.mock_init(mocker)
    pass
