import asyncio
import pytest

from ..timeout import PytestAsyncTimeout

from ...src.tcp.client import TcpClientAgen, TcpClientManage
from ...src.tcp.server import TcpServer
from ...src.exception.tcp import ConnTimeoutError, ServiceTimeoutError


LOCAL_HOST = '127.0.0.1'


class TestClient:
    @PytestAsyncTimeout(1)
    async def test_no_server(self):
        """没有服务端测试
        """
        port = 10010
        client = TcpClientManage(LOCAL_HOST, port)
        t, _ = await client.api_no_raise('')
        assert t == 'ConnTimeoutError'
        await client.close()
        pass

    @PytestAsyncTimeout(1)
    async def test_server_close(self):
        port = 10011

        async with (
            TcpServer(LOCAL_HOST, port),
            TcpClientAgen(LOCAL_HOST, port) as client
        ):
            await client.api('')
            pass
        with pytest.raises(ConnTimeoutError):
            await client.api('')
            pass
        await client.close()
        pass

    @PytestAsyncTimeout(2)
    async def test_no_server_shorter(self):
        """
        """
        port = 10012
        client = TcpClientManage(LOCAL_HOST, port, conn_timeout_base=0.01)

        # 连接失败
        with pytest.raises(ConnTimeoutError):
            await client.api('')
            pass
        # 经过短时间等待
        await asyncio.sleep(0.05)

        # 启动服务端(短期失败后重连成功)
        async with TcpServer(LOCAL_HOST, port):
            await client.wait_conn()
            await client.api('')
            pass

        await client.close()
        pass

    @PytestAsyncTimeout(4)
    async def test_no_server_longer(self):
        """长期失败后重连成功
        """
        port = 10013
        client = TcpClientManage(LOCAL_HOST, port, conn_timeout_base=0.01)

        # 连接失败
        with pytest.raises(ConnTimeoutError):
            await client.api('')
            pass
        # 经过长时间等待
        await asyncio.sleep(1)

        # 启动服务端(长期失败后重连成功)
        async with TcpServer(LOCAL_HOST, port):
            await client.wait_conn()
            await client.api('')
            pass

        await client.close()
        pass

    @PytestAsyncTimeout(2)
    async def test_map_future_del_ok(self):
        port = 10014
        async with (
            TcpServer(LOCAL_HOST, port),
            TcpClientAgen(LOCAL_HOST, port, api_delay=0.5) as client,
        ):
            await client.api('')
            await asyncio.sleep(1)
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_map_future_del_early(self):
        port = 10015
        async with (
            TcpServer(LOCAL_HOST, port),
            TcpClientAgen(LOCAL_HOST, port, api_delay=0) as client,
        ):
            with pytest.raises(ServiceTimeoutError):
                await client.api('')
            pass
        pass
    pass
