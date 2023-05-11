import asyncio

from pytest_mock import MockerFixture

from ...mock.log import MockLog

from ...src.tool.log_tool import Logger
from ...src.tool.server_tool import ServerRegister
from ...src.exception.tcp import ConnException
from ...src.tcp.client import TcpApiManage
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout
from ...src.tcp.server import server_main


LOCAL_HOST = '127.0.0.1'


class TestServer:
    """测试端口范围: 10000-10009
    """
    @PytestAsyncTimeout(3)
    async def test_not_exist(self, mocker: MockerFixture):
        mocker.patch('PyCommon.configuration.log.LoggerLocal.level_dict', new=MockLog.level_dict)
        port = 10000
        async with server_main(LOCAL_HOST, port):
            # 调用不存在的服务
            assert await FuncTool.is_await_err(TcpApiManage.service(LOCAL_HOST, port, ''), ConnException)
            pass
        await Logger.shutdown()
        pass

    @staticmethod
    @ServerRegister('test/tcp/server/timeout')
    async def func_timeout():
        return await asyncio.sleep(2)

    @PytestAsyncTimeout(4)
    async def test_service_timeout(self, mocker: MockerFixture):
        mocker.patch('PyCommon.configuration.log.LoggerLocal.level_dict', new=MockLog.level_dict)
        port = 10001
        async with server_main(LOCAL_HOST, port):
            # 调用一个超时服务-1秒超时时间
            assert await FuncTool.is_await_err(
                TcpApiManage.service(LOCAL_HOST, port, 'test/tcp/server/timeout/func_timeout'),
                ConnException,
            )
            pass
        await Logger.shutdown()
        pass

    @staticmethod
    @ServerRegister('test/tcp/server/norm')
    async def func_norm():
        return await asyncio.sleep(0.1)

    @PytestAsyncTimeout(3)
    async def test_service_norm(self, mocker: MockerFixture):
        mocker.patch('PyCommon.configuration.log.LoggerLocal.level_dict', new=MockLog.level_dict)
        port = 10002
        async with server_main(LOCAL_HOST, port):
            # 调用一个正常服务
            assert await TcpApiManage.service(LOCAL_HOST, port, 'test/tcp/server/norm/func_norm') is None
            assert await TcpApiManage.service(LOCAL_HOST, port, 'test/tcp/server/norm/func_norm') is None
            # 关闭tcp套接字
            assert await TcpApiManage.close(LOCAL_HOST, port) is None
            pass
        await Logger.shutdown()
        pass
    pass
