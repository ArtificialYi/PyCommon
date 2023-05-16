from pytest_mock import MockerFixture

from ...src.tool.func_tool import PytestAsyncTimeout


class TestLogger:
    @PytestAsyncTimeout(1)
    async def test(self, mocker: MockerFixture):
        # mocker.patch('PyCommon.configuration.log.LoggerLocal.get_logger', new=get_mock_logger)
        # assert Logger.LEVEL == LogLevel.INFO
        # Logger.set_level(LogLevel.DEBUG)
        # assert Logger.LEVEL == LogLevel.DEBUG
        # await Logger.debug('debug')
        # await Logger.warn('warn')
        # await Logger.error('error')
        # await Logger.critical('critical')
        # await Logger.shutdown()
        pass
    pass
