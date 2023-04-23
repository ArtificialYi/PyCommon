import asyncio

from ...src.tool.server_tool import ServerRegister

from ...src.exception.tcp import ConnException
from ...src.tcp.client import TcpApiManage
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout
from ...src.tcp.server import server_main
from ...src.tool.base import AsyncBase


LOCAL_HOST = '127.0.0.1'


class TestServer:
    @PytestAsyncTimeout(2)
    async def test_not_exist(self):
        port = 10001
        task = AsyncBase.coro2task_exec(server_main(LOCAL_HOST, port))
        await asyncio.sleep(1)
        # 调用不存在的服务
        assert await FuncTool.is_await_err(TcpApiManage.service(LOCAL_HOST, port, ''), ConnException)
        task.cancel()
        await FuncTool.await_no_cancel(task)
        pass

    @staticmethod
    @ServerRegister('test/timeout')
    async def func_timeout():
        return await asyncio.sleep(2)

    # @PytestAsyncTimeout(2)
    async def test_service_timeout(self):
        port = 10002
        task = AsyncBase.coro2task_exec(server_main(LOCAL_HOST, port))
        await asyncio.sleep(1)
        # 调用一个超时服务-1秒超时时间
        assert await FuncTool.is_await_err(TcpApiManage.service(LOCAL_HOST, port, 'test/timeout/func_timeout'), ConnException)
        task.cancel()
        await FuncTool.await_no_cancel(task)
        pass
    pass
