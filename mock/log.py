from pytest_mock import MockerFixture

from ..src.configuration.sync import log as sync_log
from ..src.configuration.norm import log
from ..src.tool.map_tool import MapKeyGlobal


class MockLogger:
    @staticmethod
    def mock_init(mocker: MockerFixture):
        @MapKeyGlobal(is_loop=True)
        async def get_mock_logger():
            return MockLogger()
        mocker.patch(f'{log.__name__}.LoggerLocal.get_logger', new=get_mock_logger)
        pass

    async def debug(self, *args, **kwds):
        print(*args, **kwds)
        pass

    info = warning = error = exception = debug
    pass


class MockLoggerSync:
    @staticmethod
    def mock_init(mocker: MockerFixture):
        @MapKeyGlobal(is_loop=True)
        def get_mock_logger():
            return MockLoggerSync()
        mocker.patch(f'{sync_log.__name__}.LoggerLocal.get_logger', new=get_mock_logger)
        # mocker.patch(f'{sync_log.__name__}.LoggerLocal.get_logger')
        # mocker.return_value = MockLoggerSync()
        pass

    def debug(self, *args, **kwds):
        print(*args, **kwds)
        pass

    info = warning = error = exception = debug
    pass
