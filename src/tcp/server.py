from asyncio import StreamReader, StreamWriter
import asyncio
from concurrent.futures import ALL_COMPLETED, FIRST_COMPLETED

from ..exception.tcp import ServerAlreadyStartError

from ..tool.base import AsyncBase, BaseTool
from ..tool.map_tool import LockManage, MapKey
from ...configuration.log import LoggerLocal
from ..flow.server import FlowRecv, FlowSendServer


class TcpServer:
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__task_main = AsyncBase.get_done_task()
        self.__tasks_handle = set[asyncio.Task]()
        self.__lock_main = LockManage()
        pass

    async def __tasks_await(self, tasks_flow: set[asyncio.Task], addr):
        """所有异常全都无视
        """
        try:
            done, _ = await asyncio.wait(tasks_flow, return_when=FIRST_COMPLETED)
            done.pop().result()
        except BaseException as e:
            await LoggerLocal.exception(e, f'服务端异常:{addr}: {type(e).__name__}:{e}')
        finally:
            for task_flow in tasks_flow:
                task_flow.cancel()
                pass
            await asyncio.wait(tasks_flow, return_when=ALL_COMPLETED)

    async def __handle(self, reader: StreamReader, writer: StreamWriter):
        """handle不应该抛出除了cancel以外的异常
        """
        addr = writer.get_extra_info('peername')
        await LoggerLocal.info(f'服务端：Connection from {addr}')

        task_handle: asyncio.Task = asyncio.current_task()  # type: ignore
        self.__tasks_handle.add(task_handle)

        try:
            async with (
                FlowSendServer(writer) as flow_send,
                FlowRecv(reader, flow_send) as flow_recv,
            ):
                tasks_flow = {flow_send.task, flow_recv.task}
                try:
                    await self.__tasks_await(tasks_flow, addr)
                finally:
                    writer.close()
                    await LoggerLocal.info(f'服务端：TCP连接关闭:{addr}-开始')
                    # 如果在此处任务被取消，那么 TCP连接关闭-结束 的日志将不会打印
                    await writer.wait_closed()
                    await LoggerLocal.info(f'服务端：TCP连接关闭:{addr}-结束')
        finally:
            self.__tasks_handle.remove(task_handle)

    @MapKey(BaseTool.return_self)
    async def __get_server(self) -> asyncio.Server:
        return await asyncio.start_server(self.__handle, self.__host, self.__port,)

    async def __handle_await(self):
        # 主动关闭的起点和终点
        for task_handle in self.__tasks_handle:
            task_handle.cancel()
        if len(self.__tasks_handle) > 0:
            await asyncio.wait(self.__tasks_handle, return_when=ALL_COMPLETED)
        pass

    async def __start(self):
        server: asyncio.Server = await self.__get_server()
        try:
            async with server:  # pragma: no cover
                await server.serve_forever()
        except asyncio.CancelledError:
            await LoggerLocal.warning('服务端：forever-handle取消+等待ing')
            await self.__handle_await()
            await LoggerLocal.warning('服务端：forever-handle全部取消')
            raise

    async def start(self):
        """同一时间只能启动一个task
        """
        if not self.__task_main.done():
            raise ServerAlreadyStartError(f'已经启动了一个服务:{self.__host}:{self.__port}')
        self.__task_main = asyncio.create_task(self.__start())
        await self.__get_server()
        return self

    async def close(self):
        if self.__task_main.done():
            return

        async with self.__lock_main.get_lock():
            if self.__task_main.done():
                return

            server: asyncio.Server = await self.__get_server()
            server.close()
            await LoggerLocal.info('服务端：主动关闭服务-开始')
            await asyncio.wait({self.__task_main}, return_when=ALL_COMPLETED)
            await LoggerLocal.info('服务端：主动关闭服务-结束')
            pass
        pass

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.close()
    pass
