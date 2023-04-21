from ...src.tcp.client import TcpApiManage
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout


LOCAL_HOST = '127.0.0.1'


class TestClient:
    @PytestAsyncTimeout(1)
    async def test_client_no_server(self):
        host = LOCAL_HOST
        port = 10000
        assert await FuncTool.is_await_err(TcpApiManage.service(host, port, ''), ConnectionRefusedError)
        pass
    pass
