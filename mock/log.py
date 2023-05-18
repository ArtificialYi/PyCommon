from pytest_mock import MockerFixture

from ..configuration import log
from ..src.tool.map_tool import MapKey


class MockLogger:
    @staticmethod
    def mock_init(mocker: MockerFixture):
        @MapKey()
        async def get_mock_logger():
            return MockLogger()
        mocker.patch(f'{log.__name__}.LoggerLocal.get_logger', new=get_mock_logger)
        pass

    async def debug(self, *args, **kwds):
        print(*args, **kwds)
        pass

    info = warning = error = exception = debug
    pass
