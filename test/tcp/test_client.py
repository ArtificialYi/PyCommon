from pytest_mock import MockerFixture
from asyncio.exceptions import TimeoutError

from ...mock.log import get_mock_logger
from ...src.tcp.client import TcpApiManage
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout


LOCAL_HOST = '127.0.0.1'


class TestClient:
    @PytestAsyncTimeout(1)
    async def test_client_no_server(self, mocker: MockerFixture):
        mocker.patch('PyCommon.configuration.log.LoggerLocal.get_logger', new=get_mock_logger)
        port = 10010
        assert await FuncTool.is_await_err(TcpApiManage.service(LOCAL_HOST, port, ''), TimeoutError)
        pass
    pass
