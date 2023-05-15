from asyncio import StreamReader, StreamWriter
import asyncio
from concurrent.futures import ALL_COMPLETED, FIRST_COMPLETED

from ..tool.base import AsyncBase, BaseTool
from ..tool.map_tool import MapKey
from ...configuration.log import LoggerLocal
from ..flow.server import FlowJsonDeal, FlowRecv, FlowSendServer


class ServerTcp:
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__task_main = AsyncBase.get_done_task()
        self.__tasks_handle = set[asyncio.Task]()
        pass

    async def __tasks_await(self, tasks_flow: set[asyncio.Task], addr):
        try:
            done, _ = await asyncio.wait(tasks_flow, return_when=FIRST_COMPLETED)
            done.pop().result()
        except BaseException as e:
            await LoggerLocal.exception(e, f'服务端关闭:Connection from {addr} is closing: {type(e).__name__}:{e}')
            raise
        finally:
            for task_flow in tasks_flow:
                task_flow.cancel()
                pass
            await asyncio.wait(tasks_flow, return_when=ALL_COMPLETED)
            pass
        pass

    async def __handle(self, reader: StreamReader, writer: StreamWriter):
        addr = writer.get_extra_info('peername')
        await LoggerLocal.info(f'服务端：Connection from {addr}')

        task_handle: asyncio.Task = asyncio.current_task()  # type: ignore
        self.__tasks_handle.add(task_handle)

        try:
            async with (
                FlowSendServer(writer) as flow_send,
                FlowJsonDeal(flow_send) as flow_json,
                FlowRecv(reader, flow_json) as flow_recv,
            ):
                tasks_flow = {flow_send.task, flow_json.task, flow_recv.task}
                try:
                    await self.__tasks_await(tasks_flow, addr)
                    pass
                finally:
                    writer.close()
                    await writer.wait_closed()
                    await LoggerLocal.info('服务端：Closed the connection')
                pass
            pass
        finally:
            self.__tasks_handle.remove(task_handle)
        pass

    @MapKey(BaseTool.return_self)
    async def __get_server(self) -> asyncio.Server:
        return await asyncio.start_server(self.__handle, self.__host, self.__port,)

    async def __handle_await(self):
        for task_handle in self.__tasks_handle:
            task_handle.cancel()
        await asyncio.wait(self.__tasks_handle, return_when=ALL_COMPLETED)

    async def __start(self):
        server: asyncio.Server = await self.__get_server()
        try:
            async with server:
                await server.serve_forever()
                pass
            pass
        except asyncio.CancelledError:
            await LoggerLocal.warning('服务端：server is closing')
            await self.__handle_await()
            await LoggerLocal.warning('服务端：server is closed')
            raise
        pass

    async def start(self, delay: float = 1):
        """同一时间只能启动一个task

        Returns:
            _type_: _description_
        """
        if not self.__task_main.done():
            raise Exception(f'已经启动了一个服务:{self.__host}:{self.__port}')
        self.__task_main = asyncio.create_task(self.__start())
        await asyncio.sleep(delay)
        return self

    async def close(self, delay: float = 1):
        server: asyncio.Server = await self.__get_server()
        server.close()
        await server.wait_closed()
        await asyncio.sleep(delay)
        pass
    pass
