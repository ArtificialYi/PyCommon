from pytest_mock import MockerFixture
from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.tool.log_tool import Logger
from ...mock.log import MockLog
from aiologger.levels import LogLevel


class TestLogger:
    @PytestAsyncTimeout(1)
    async def test(self, mocker: MockerFixture):
        mocker.patch('PyCommon.configuration.log.LoggerLocal.level_dict', new=MockLog.level_dict)
        assert Logger.LEVEL == LogLevel.INFO
        Logger.set_level(LogLevel.DEBUG)
        assert Logger.LEVEL == LogLevel.DEBUG
        await Logger.debug('debug')
        await Logger.warn('warn')
        await Logger.error('error')
        await Logger.critical('critical')
        await Logger.shutdown()
        pass
    pass
