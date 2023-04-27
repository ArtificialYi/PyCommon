from ...src.tcp.client import TcpApiManage
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout


LOCAL_HOST = '127.0.0.1'


class TestClient:
    @PytestAsyncTimeout(1)
    async def test_client_no_server(self):
        port = 10010
        assert await FuncTool.is_await_err(TcpApiManage.service(LOCAL_HOST, port, ''), ConnectionRefusedError)
        pass
    pass
