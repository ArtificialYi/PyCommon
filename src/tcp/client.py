import asyncio
from typing import Tuple

from ..tool.map_tool import MapKey

from ..tool.base import AsyncBase
from ..flow.base import FlowRecv
from ..tool.func_tool import QueueException
from ..flow.client import FlowJsonDealForClient, FlowSendClient


class TcpApi:
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__task = None
        self.__lock = None
        pass

    async def __flow_run(self, future: asyncio.Future):
        reader, writer = await asyncio.open_connection(self.__host, self.__port)
        try:
            err_queue = QueueException()
            future_map = dict()
            async with (
                FlowSendClient(writer, err_queue) as flow_send,
                FlowJsonDealForClient(future_map, err_queue) as flow_json,
                FlowRecv(reader, flow_json, err_queue),
            ):
                future.set_result((flow_send, future_map))
                await err_queue.exception_loop()
                pass
            pass
        except Exception as e:
            # TODO: 此处需记录每次断开连接的原因
            print(e)
            raise e
        finally:
            writer.close()
            await writer.wait_closed()
            pass
        pass

    def __get_lock(self):
        if self.__lock is None:
            self.__lock = asyncio.Lock()
        return self.__lock

    def __next_id(self):
        self.__tcp_id += 1
        return self.__tcp_id

    async def __get_flow_send(self) -> Tuple[FlowSendClient, int, dict]:
        async with self.__get_lock():
            if self.__task is None or self.__task.done():
                future: asyncio.Future[Tuple[FlowSendClient, dict]] = asyncio.Future()
                self.__task = AsyncBase.coro2task_exec(self.__flow_run(future))
                self.__flow_send, self.__future_map = await future
                self.__tcp_id = 0
                pass
            pass
        tcp_id = self.__next_id()
        return self.__flow_send, tcp_id, self.__future_map

    async def api(self, path: str, *args, **kwds):
        flow_send, tcp_id, future_map = await self.__get_flow_send()
        # 添加id映射
        future_map[tcp_id] = asyncio.Future()
        await flow_send.send(tcp_id, path, *args, **kwds)
        try:
            return await asyncio.wait_for(future_map[tcp_id], 10)
        finally:
            del future_map[tcp_id]
    pass


class TcpApiManage:
    @staticmethod
    @MapKey(lambda host, port: f'{host}:{port}')
    def get_tcp(host: str, port: int) -> TcpApi:
        return TcpApi(host, port)
    pass
