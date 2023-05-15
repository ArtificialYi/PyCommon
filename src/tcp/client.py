import asyncio
from concurrent.futures import ALL_COMPLETED, FIRST_COMPLETED
from typing import Optional, Tuple
from asyncio import StreamReader, StreamWriter

from ..exception.tcp import ConnTimeoutError, ServiceTimeoutError

from ...configuration.log import LoggerLocal

from ..tool.loop_tool import LoopExecBg
from ..tool.map_tool import MapKey
from ..tool.base import AsyncBase
from ..flow.client import JsonDeal, FlowSendClient, FlowRecv


class TcpConn:
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        pass

    @property
    def host(self) -> str:
        return self.__host

    @property
    def port(self) -> int:
        return self.__port

    async def __conn_unit(self):
        try:
            return await asyncio.open_connection(self.__host, self.__port)
        except Exception as e:
            # TODO: 此处需记录断开连接的原因
            await LoggerLocal.warning(f'连接失败原因:{e}')
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
            await LoggerLocal.error(f'TCP服务连接失败:{self.__host}:{self.__port}')
            await asyncio.sleep(60)
        return reader, writer

    async def conn(self) -> Tuple[StreamReader, StreamWriter]:
        reader, writer = await self.__conn_warn()
        if reader is None or writer is None:
            reader, writer = await self.__conn_error()
        return reader, writer
    pass


class TcpSend:
    def __init__(self, host: str, port: int, api_delay: float = 2) -> None:
        self.__conn = TcpConn(host, port)
        self.__loop_bg = LoopExecBg(self.__flow_run)
        self.__loop_bg.run()
        self.__future: asyncio.Future[FlowSendClient] = AsyncBase.get_future()

        self.__api_delay = api_delay
        self.__tcp_id = 0
        pass

    async def __flow_run(self):
        reader, writer = await self.__conn.conn()
        async with (
            FlowSendClient(writer, self.__api_delay * 2) as flow_send,
            FlowRecv(reader, JsonDeal(flow_send.future_map)) as flow_recv,
        ):
            self.__future.set_result(flow_send)
            tasks_flow = {flow_send.task, flow_recv.task}
            try:
                done, _ = await asyncio.wait(tasks_flow, return_when=FIRST_COMPLETED)
                done.pop().result()
            except BaseException as e:
                # TODO: 此处需记录断开连接的原因
                await LoggerLocal.exception(e, f'客户端关闭:{self.__conn.host}:{self.__conn.port}|{type(e).__name__}|{e}')
                raise
            finally:
                for task_flow in tasks_flow:
                    task_flow.cancel()
                self.__future = AsyncBase.get_future()
                writer.close()
                task_close = asyncio.create_task(writer.wait_closed())
                await asyncio.wait({*tasks_flow, task_close}, return_when=ALL_COMPLETED)
                pass
            pass
        pass

    async def close(self):
        await self.__loop_bg.stop()
        pass

    async def __get_flow_send(self):
        try:
            return await asyncio.wait_for(self.__future, 0.1) if not self.__future.done() else await self.__future
        except asyncio.TimeoutError:
            raise ConnTimeoutError(f'连接服务端超时:{self.__conn.host}:{self.__conn.port}')

    def __next_id(self):
        self.__tcp_id += 1
        return self.__tcp_id

    async def api(self, path: str, *args, **kwds):
        flow_send = await self.__get_flow_send()
        tcp_id = self.__next_id()
        future = await flow_send.send(tcp_id, path, *args, **kwds)
        try:
            res = await asyncio.wait_for(future, self.__api_delay)
            return res
        except asyncio.TimeoutError:
            raise ServiceTimeoutError(f'服务调用超时:{self.__conn.host}:{self.__conn.port}:{path}:{args}:{kwds}')
        except BaseException:
            raise
    pass


class TcpApiManage:
    @staticmethod
    @MapKey(lambda host, port: f'{host}:{port}')
    def __get_tcp(host: str, port: int) -> TcpSend:
        return TcpSend(host, port)

    @staticmethod
    async def service(host: str, port: int, path: str, *args, **kwds):
        tcp: TcpSend = TcpApiManage.__get_tcp(host, port)
        return await tcp.api(path, *args, **kwds)

    @staticmethod
    async def close(host: str, port: int):
        tcp: TcpSend = TcpApiManage.__get_tcp(host, port)
        return await tcp.close()
    pass
