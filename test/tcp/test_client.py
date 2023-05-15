import pytest

from ...src.exception.tcp import ConnTimeoutError
from ...src.tcp.client import TcpApiManage
from ...src.tool.func_tool import PytestAsyncTimeout


LOCAL_HOST = '127.0.0.1'


class TestClient:
    @PytestAsyncTimeout(1)
    async def test_client_no_server(self):
        port = 10010
        with pytest.raises(ConnTimeoutError):
            await TcpApiManage.service(LOCAL_HOST, port, '')
        await TcpApiManage.close(LOCAL_HOST, port)
        pass
    pass
