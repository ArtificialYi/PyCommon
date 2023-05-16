import asyncio
import pytest

from ...src.exception.tcp import ServerAlreadyStartError, ServiceTimeoutError
from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.tcp.client import TcpClientManage
from ...src.tool.server_tool import ServerRegister
from ...src.tcp.server import ServerTcp


LOCAL_HOST = '127.0.0.1'


class TestServer:
    """测试端口范围: 10000-10009
    """

    @PytestAsyncTimeout(1)
    async def test_err(self):
        port = 10000
        server = ServerTcp(LOCAL_HOST, port)
        # 同时启动两个会报错
        with pytest.raises(ServerAlreadyStartError):
            await asyncio.gather(server.start(), server.start(),)

        # 同时关闭两个没有影响
        await asyncio.gather(server.close(), server.close(),)
        # 双检锁
        await server.close()
        pass

    @PytestAsyncTimeout(1)
    async def test_not_exist(self):
        port = 10000
        server = await ServerTcp(LOCAL_HOST, port).start()
        # # 调用不存在的服务
        async with TcpClientManage(LOCAL_HOST, port) as client:
            res = await client.api('')
            assert res.get('type') == 'ServiceNotFoundException'
        await server.close()
        pass

    @staticmethod
    @ServerRegister('test/tcp/server/timeout')
    async def func_timeout():
        return await asyncio.sleep(2)

    @PytestAsyncTimeout(3)
    async def test_service_timeout(self):
        port = 10001
        server = await ServerTcp(LOCAL_HOST, port).start()
        # 调用一个超时服务-2秒超时时间
        with pytest.raises(ServiceTimeoutError):
            async with TcpClientManage(LOCAL_HOST, port) as client:
                await client.api('test/tcp/server/timeout/func_timeout')
        await server.close()
        pass

    @staticmethod
    @ServerRegister('test/tcp/server/norm')
    async def func_norm():
        await asyncio.sleep(0.1)
        return True

    @PytestAsyncTimeout(1)
    async def test_service_norm(self):
        port = 10002
        server = await ServerTcp(LOCAL_HOST, port).start()
        async with TcpClientManage(LOCAL_HOST, port) as client:
            assert await client.api('test/tcp/server/norm/func_norm') is True
            assert await client.api('test/tcp/server/norm/func_norm') is True
        # 关闭tcp套接字
        await server.close()
        pass
    pass
