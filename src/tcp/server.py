from asyncio import StreamReader, StreamWriter
import asyncio
from concurrent.futures import ALL_COMPLETED, FIRST_COMPLETED

from ..exception.tcp import ServerAlreadyStartError
from ..tool.base import AsyncBase
from ..tool.map_tool import LockManage
from ...configuration.log import LoggerLocal
from ..flow.server import FlowRecv, FlowSendServer


class ServerFlow:
    def __init__(self, reader: StreamReader, writer: StreamWriter) -> None:
        self.__reader = reader
        self.__writer = writer
        self.__addr = writer.get_extra_info('peername')
        pass

    async def flow(self):
        await LoggerLocal.info(f'服务端：Connection from {self.__addr}')

        async with (
            FlowSendServer(self.__writer) as flow_send,
            FlowRecv(self.__reader, flow_send) as flow_recv,
        ):
            tasks_flow = {flow_send.task, flow_recv.task}
            try:
                done, _ = await asyncio.wait(tasks_flow, return_when=FIRST_COMPLETED)
                done.pop().result()
            except BaseException as e:
                await LoggerLocal.exception(e, f'服务端异常:{self.__addr}: {type(e).__name__}:{e}')
            finally:
                for task_flow in tasks_flow:
                    task_flow.cancel()
                    pass
                self.__writer.close()
                await LoggerLocal.info(f'服务端：TCP连接关闭:{self.__addr}-开始')
                # 如果在此处任务被取消，那么 TCP连接关闭-结束 的日志将不会打印
                await asyncio.wait(tasks_flow, return_when=ALL_COMPLETED)
                await self.__writer.wait_closed()
                await LoggerLocal.info(f'服务端：TCP连接关闭:{self.__addr}-结束')
    pass


class ServerHandle:
    def __init__(self) -> None:
        self.__tasks = set[asyncio.Task]()
        pass

    async def handle(self, reader: StreamReader, writer: StreamWriter):
        """handle不应该抛出除了cancel以外的异常
        """
        task: asyncio.Task = asyncio.current_task()  # type: ignore
        self.__tasks.add(task)
        try:
            await ServerFlow(reader, writer).flow()
        finally:
            self.__tasks.remove(task)
        pass

    async def close_all(self):
        for task in self.__tasks:
            task.cancel()
        if len(self.__tasks) > 0:
            await asyncio.wait(self.__tasks, return_when=ALL_COMPLETED)
    pass


class ServerForever:
    def __init__(self) -> None:
        self.__futures = set[asyncio.Future[asyncio.Server]]()
        pass

    async def forever(self, host: str, port: int, future: asyncio.Future[asyncio.Server]):
        self.__futures.add(future)
        handle = ServerHandle()
        try:
            server = await asyncio.start_server(handle.handle, host, port)
            async with server:  # pragma: no cover
                future.set_result(server)
                await server.serve_forever()
        except asyncio.CancelledError:
            await LoggerLocal.warning('服务端：forever-handle取消+等待ing')
            await handle.close_all()
            await LoggerLocal.warning('服务端：forever-handle全部取消')
            raise

    async def close_all(self):
        while self.__futures:
            server = await self.__futures.pop()
            server.close()
            await server.wait_closed()
    pass


class TcpServer:
    def __init__(self, host: str, port: int) -> None:
        self.__task = AsyncBase.get_done_task()
        self.__host = host
        self.__port = port
        self.__forever = ServerForever()
        self.__lock = LockManage()
        pass

    def __await__(self):
        yield from self.__task

    async def start(self):
        if not self.__task.done():
            raise ServerAlreadyStartError(f'已经启动了一个服务:{self.__host}:{self.__port}')
        future = AsyncBase.get_future()
        self.__task = asyncio.create_task(self.__forever.forever(self.__host, self.__port, future))
        await future
        return self

    async def close(self):
        if self.__task.done():
            return

        async with self.__lock.get_lock():
            if self.__task.done():
                return

            await self.__forever.close_all()
            await LoggerLocal.info('服务端：主动关闭服务-开始')
            await asyncio.wait({self.__task}, return_when=ALL_COMPLETED)
            await LoggerLocal.info('服务端：主动关闭服务-结束')
            pass
        pass

    async def __aenter__(self):
        return await self.start()

    async def __aexit__(self, *args):
        await self.close()
    pass
