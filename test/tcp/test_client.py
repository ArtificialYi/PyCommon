import asyncio
import pytest

from ...src.tcp.server import TcpServer

from ...src.exception.tcp import ConnTimeoutError, ServiceTimeoutError
from ...src.tcp.client import TcpClientManage
from ...src.tool.func_tool import PytestAsyncTimeout


LOCAL_HOST = '127.0.0.1'


class TestClient:
    @PytestAsyncTimeout(1)
    async def test_no_server(self):
        port = 10010
        async with TcpClientManage(LOCAL_HOST, port) as client:
            t, _ = await client.api_no_raise('')
            assert t == 'ConnTimeoutError'
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_server_close(self):
        port = 10011
        # 启动服务
        server = await TcpServer(LOCAL_HOST, port).start()
        async with TcpClientManage(LOCAL_HOST, port) as client:
            await client.api('')
            # 关闭服务
            await server.close()
            with pytest.raises(ConnTimeoutError):
                await client.api('')
            pass
        pass

    @PytestAsyncTimeout(2)
    async def test_no_server_longer(self):
        port = 10012
        async with TcpClientManage(LOCAL_HOST, port, conn_timeout_base=0.01) as client:
            # 连接失败
            with pytest.raises(ConnTimeoutError):
                await client.api('')
                pass
            # 经过长时间等待
            await asyncio.sleep(1)

            # 启动服务端
            async with TcpServer(LOCAL_HOST, port):
                await client.wait_conn()
                await client.api('')
                pass
            pass
        pass

    @PytestAsyncTimeout(2)
    async def test_map_future_del_ok(self):
        port = 10013
        async with (
            TcpServer(LOCAL_HOST, port),
            TcpClientManage(LOCAL_HOST, port, api_delay=0.5) as client,
        ):
            await client.api('')
            await asyncio.sleep(1)
            pass

    @PytestAsyncTimeout(1)
    async def test_map_future_del_early(self):
        port = 10013
        async with (
            TcpServer(LOCAL_HOST, port),
            TcpClientManage(LOCAL_HOST, port, api_delay=0) as client,
        ):
            with pytest.raises(ServiceTimeoutError):
                await client.api('')
            pass
    pass
