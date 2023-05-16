import pytest

from ...src.tcp.server import ServerTcp

from ...src.exception.tcp import ConnTimeoutError
from ...src.tcp.client import TcpClientManage
from ...src.tool.func_tool import PytestAsyncTimeout


LOCAL_HOST = '127.0.0.1'


class TestClient:
    @PytestAsyncTimeout(1)
    async def test_client_no_server(self):
        port = 10010
        with pytest.raises(ConnTimeoutError):
            async with TcpClientManage(LOCAL_HOST, port) as client:
                await client.api('')
                pass
            pass
        pass

    # @PytestAsyncTimeout(1)
    async def test_server_close(self):
        port = 10011
        # 启动服务
        server = await ServerTcp(LOCAL_HOST, port).start()
        async with TcpClientManage(LOCAL_HOST, port) as client:
            await client.api('')
            # 关闭服务
            await server.close()
            with pytest.raises(ConnTimeoutError):
                await client.api('')
            pass
        pass
    pass
