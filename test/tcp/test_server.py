import asyncio
import pytest

from pytest_mock import MockerFixture

from ...src.exception.tcp import ServiceTimeoutError

from ...configuration.log import LoggerLocal

from ...mock.log import get_mock_logger

from ...src.tool.server_tool import ServerRegister
from ...src.tcp.client import TcpApiManage
from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.tcp.server import server_main


LOCAL_HOST = '127.0.0.1'


class TestServer:
    """测试端口范围: 10000-10009
    """
    @PytestAsyncTimeout(3)
    async def test_not_exist(self, mocker: MockerFixture):
        mocker.patch('PyCommon.configuration.log.LoggerLocal.get_logger', new=get_mock_logger)
        port = 10000
        async with server_main(LOCAL_HOST, port):
            # 调用不存在的服务
            res = await TcpApiManage.service(LOCAL_HOST, port, '')
            assert res.get('type') == 'ServiceNotFoundException'
            TcpApiManage.close(LOCAL_HOST, port)
            pass
        await LoggerLocal.shutdown()
        pass

    @staticmethod
    @ServerRegister('test/tcp/server/timeout')
    async def func_timeout():
        return await asyncio.sleep(2)

    @PytestAsyncTimeout(5)
    async def test_service_timeout(self, mocker: MockerFixture):
        mocker.patch('PyCommon.configuration.log.LoggerLocal.get_logger', new=get_mock_logger)
        port = 10001
        async with server_main(LOCAL_HOST, port):
            # 调用一个超时服务-2秒超时时间
            with pytest.raises(ServiceTimeoutError):
                await TcpApiManage.service(LOCAL_HOST, port, 'test/tcp/server/timeout/func_timeout')
                pass
            TcpApiManage.close(LOCAL_HOST, port)
            pass
        await LoggerLocal.shutdown()
        pass

    @staticmethod
    @ServerRegister('test/tcp/server/norm')
    async def func_norm():
        await asyncio.sleep(0.1)
        return True

    # @PytestAsyncTimeout(3)
    async def test_service_norm(self, mocker: MockerFixture):
        mocker.patch('PyCommon.configuration.log.LoggerLocal.get_logger', new=get_mock_logger)
        port = 10002
        async with server_main(LOCAL_HOST, port):
            # 调用一个正常服务
            assert await TcpApiManage.service(LOCAL_HOST, port, 'test/tcp/server/norm/func_norm') is True
            assert await TcpApiManage.service(LOCAL_HOST, port, 'test/tcp/server/norm/func_norm') is True
            # 关闭tcp套接字
            TcpApiManage.close(LOCAL_HOST, port)
            pass
        await LoggerLocal.shutdown()
        pass
    pass
