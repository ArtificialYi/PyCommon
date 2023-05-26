import asyncio
import pytest

from ..timeout import PytestAsyncTimeout
from ...src.tool.base import AsyncBase
from ...src.exception.tcp import ServerAlreadyStartError, ServiceTimeoutError
from ...src.tcp.client import TcpClientManage
from ...src.tool.server_tool import ServerRegister
from ...src.tcp.server import TcpServer


LOCAL_HOST = '127.0.0.1'


class TestServer:
    """测试端口范围: 10000-10009
    """

    # @PytestAsyncTimeout(1)
    async def test_err(self):
        port = 10000
        server = TcpServer(LOCAL_HOST, port)
        # 同时启动两个会报错
        with pytest.raises(ServerAlreadyStartError):
            await asyncio.gather(server.start(), server.start(),)

        # 启动中的server不会主动结束
        assert not await AsyncBase.wait_done(server.task, 0.1)

        # 同时关闭两个没有影响
        await asyncio.gather(server.close(), server.close(),)
        # 双检锁
        await server.close()

        # 已经关闭的服务
        with pytest.raises(asyncio.CancelledError):
            await server.task
        pass

    @PytestAsyncTimeout(1)
    async def test_not_exist(self):
        port = 10000
        # # 调用不存在的服务
        async with (
            TcpServer(LOCAL_HOST, port),
            TcpClientManage(LOCAL_HOST, port) as client,
        ):
            t, data = await client.api('')
            assert t == 'ServiceNotFoundException'
            assert data == '服务不存在:'
        pass

    @staticmethod
    @ServerRegister('test/tcp/server/timeout')
    async def func_timeout():
        return await asyncio.sleep(2)

    @PytestAsyncTimeout(3)
    async def test_service_timeout(self):
        port = 10001
        async with (
            TcpServer(LOCAL_HOST, port),
            TcpClientManage(LOCAL_HOST, port) as client
        ):
            with pytest.raises(ServiceTimeoutError):
                await client.api('test/tcp/server/timeout/func_timeout')
        pass

    @staticmethod
    @ServerRegister('test/tcp/server/norm')
    async def func_norm():
        await asyncio.sleep(0.1)
        return True

    @PytestAsyncTimeout(1)
    async def test_service_norm(self):
        port = 10002
        async with (
            TcpServer(LOCAL_HOST, port),
            TcpClientManage(LOCAL_HOST, port) as client
        ):
            t, data = await client.api('test/tcp/server/norm/func_norm')
            assert t == 'bool'
            assert data is True
            t, data = await client.api('test/tcp/server/norm/func_norm')
            assert t == 'bool'
            assert data is True
        pass
    pass
