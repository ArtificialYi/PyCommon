import asyncio

from ...src.exception.tcp import ConnException
from ...src.tcp.client import TcpApiManage
from ...src.tool.func_tool import FuncTool
from ...src.tcp.server import server_main
from ...src.tool.base import AsyncBase


LOCAL_HOST = '127.0.0.1'


class TestServer:
    async def test(self):
        port = 10001
        task = AsyncBase.coro2task_exec(server_main(LOCAL_HOST, port))
        await asyncio.sleep(1)
        # 调用不存在的服务
        assert await FuncTool.is_await_err(TcpApiManage.service(LOCAL_HOST, port, ''), ConnException)
        task.cancel()
        await FuncTool.await_no_cancel(task)
        pass
    pass
