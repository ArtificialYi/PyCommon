import pytest
from pytest_mock import MockerFixture

from ..mock.log import get_mock_logger


@pytest.fixture(autouse=True)
def logger_pre(mocker: MockerFixture):
    mocker.patch('PyCommon.configuration.log.LoggerLocal.get_logger', new=get_mock_logger)
    pass
