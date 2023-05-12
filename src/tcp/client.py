import asyncio
from concurrent.futures import FIRST_COMPLETED
from typing import Dict, Optional, Tuple
from asyncio import StreamReader, StreamWriter

from ..tool.loop_tool import LoopExecBg
from ..tool.map_tool import MapKey
from ..tool.base import AsyncBase
from ..flow.client import JsonDeal, FlowSendClient, FlowRecv


class TcpApi:
    """TCP实际开放的API
    """
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__tcp_id = 0

        self.__loop_bg = LoopExecBg(self.__flow_run)
        self.__loop_bg.run()

        self.__future: asyncio.Future[FlowSendClient] = AsyncBase.get_future()
        self.__future_map: Dict[int, asyncio.Future] = dict()
        pass

    async def __conn_unit(self):
        try:
            return await asyncio.open_connection(self.__host, self.__port)
        except BaseException as e:
            # TODO: 此处需记录断开连接的原因
            print(e)
            return None, None

    async def __conn_warn(self) -> Tuple[Optional[StreamReader], Optional[StreamWriter]]:
        # retry重连机制
        reader, writer = None, None
        for i in range(6):
            reader, writer = await self.__conn_unit()
            if reader is not None and writer is not None:
                break
            await asyncio.sleep(2 ** i)
        return reader, writer

    async def __conn_error(self) -> Tuple[StreamReader, StreamWriter]:
        # 严重错误告警
        while True:
            reader, writer = await self.__conn_unit()
            if reader is not None and writer is not None:
                break
            # TODO: 严重错误告警
            await asyncio.sleep(60)
        return reader, writer

    async def __conn(self) -> Tuple[StreamReader, StreamWriter]:
        reader, writer = await self.__conn_warn()
        if reader is None or writer is None:
            reader, writer = await self.__conn_error()
        return reader, writer

    async def __flow_run(self):
        reader, writer = await self.__conn()
        deal = JsonDeal(self.__future_map)
        async with (
            FlowSendClient(writer) as flow_send,
            FlowRecv(reader, deal) as flow_recv,
        ):
            self.__future.set_result(flow_send)
            done, _ = await asyncio.wait([flow_send, flow_recv], return_when=FIRST_COMPLETED)
            pass
        self.__future = AsyncBase.get_future()
        try:
            done.pop().result()
        except BaseException as e:
            # TODO: 此处需记录断开连接的原因
            print(e)
            pass
        finally:
            writer.close()
            await writer.wait_closed()
            pass
        pass

    async def close(self):
        await self.__loop_bg.stop()
        pass

    def __next_id(self):
        self.__tcp_id += 1
        return self.__tcp_id

    async def api(self, path: str, *args, **kwds):
        flow_send = await asyncio.wait_for(self.__future, 1) if not self.__future.done() else await self.__future
        tcp_id = self.__next_id()
        self.__future_map[tcp_id] = AsyncBase.get_future()
        try:
            await flow_send.send(tcp_id, path, *args, **kwds)
            return await asyncio.wait_for(self.__future_map[tcp_id], 2)
        finally:
            del self.__future_map[tcp_id]
    pass


class TcpApiManage:
    @staticmethod
    @MapKey(lambda host, port: f'{host}:{port}')
    def __get_tcp(host: str, port: int) -> TcpApi:
        return TcpApi(host, port)

    @staticmethod
    async def service(host: str, port: int, path: str, *args, **kwds):
        tcp: TcpApi = TcpApiManage.__get_tcp(host, port)
        return await tcp.api(path, *args, **kwds)

    @staticmethod
    async def close(host: str, port: int):
        tcp: TcpApi = TcpApiManage.__get_tcp(host, port)
        return await tcp.close()
    pass
