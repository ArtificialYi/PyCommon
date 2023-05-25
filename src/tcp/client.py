import asyncio
from concurrent.futures import ALL_COMPLETED, FIRST_COMPLETED
from typing import Dict, Optional, Tuple
from asyncio import StreamReader, StreamWriter

from ..configuration.env import get_value_by_tag_and_field

from ..tool.func_tool import ExceptTool
from ..exception.tcp import ConnTimeoutError, ServiceTimeoutError
from ..configuration.log import LoggerLocal
from ..tool.loop_tool import LoopExecBg
from ..tool.map_tool import MapKey
from ..tool.base import AsyncBase
from ..flow.client import FlowSendClient, FlowRecvClient


class TcpConn:
    def __init__(self, host: str, port: int, base: float = 1) -> None:
        self.__host = host
        self.__port = port
        self.__base = base
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
        except BaseException as e:
            await LoggerLocal.exception(e, f'连接失败原因:{type(e).__name__}|{e}')
            ExceptTool.raise_not_exception(e)
            return None, None

    async def __conn_warn(self) -> Tuple[Optional[StreamReader], Optional[StreamWriter]]:
        # retry重连机制
        reader, writer = None, None
        for i in range(6):
            reader, writer = await self.__conn_unit()
            if reader is not None and writer is not None:
                break
            await asyncio.sleep(2**i * self.__base)
        return reader, writer

    async def __conn_error(self) -> Tuple[StreamReader, StreamWriter]:
        # 严重错误告警
        while True:
            reader, writer = await self.__conn_unit()
            if reader is not None and writer is not None:
                break
            await LoggerLocal.error(f'TCP服务连接失败:{self.__host}:{self.__port}')
            await asyncio.sleep(60 * self.__base)
        return reader, writer

    async def conn(self) -> Tuple[StreamReader, StreamWriter]:
        reader, writer = await self.__conn_warn()
        if reader is None or writer is None:
            reader, writer = await self.__conn_error()
        return reader, writer
    pass


class TcpClient:
    def __init__(self, host: str, port: int, api_delay: float = 2, conn_timeout_base: float = 1) -> None:
        self.__conn = TcpConn(host, port, conn_timeout_base)
        self.__loop_bg = LoopExecBg(self.__flow_run)
        self.__loop_bg.run()
        self.__future: asyncio.Future[Tuple[FlowSendClient, FlowRecvClient]] = AsyncBase.get_future()

        self.__api_delay = api_delay
        pass

    async def __flow_run(self):
        reader, writer = await self.__conn.conn()
        async with (
            FlowSendClient(writer) as flow_send,
            FlowRecvClient(reader) as flow_recv,
        ):
            self.__future.set_result((flow_send, flow_recv))
            tasks_flow = {flow_send.task, flow_recv.task}
            try:
                done, _ = await asyncio.wait(tasks_flow, return_when=FIRST_COMPLETED)
                done.pop().result()
            except BaseException as e:
                await LoggerLocal.exception(e, f'客户端异常:{self.__conn.host}:{self.__conn.port}|{type(e).__name__}|{e}')
                raise
            finally:
                for task_flow in tasks_flow:
                    task_flow.cancel()
                self.__future = AsyncBase.get_future()
                writer.close()
                task_close = asyncio.create_task(writer.wait_closed())
                await asyncio.wait({*tasks_flow, task_close}, return_when=ALL_COMPLETED)

    async def close(self):
        await self.__loop_bg.stop()
        pass

    async def __get_flow(self) -> Tuple[FlowSendClient, FlowRecvClient]:
        if await AsyncBase.wait_done(self.__future, 0.1):
            return await self.__future
        raise ConnTimeoutError(f'连接服务端超时:{self.__conn.host}:{self.__conn.port}')

    async def wait_conn(self):
        return await asyncio.wait({self.__future})

    async def api(self, path: str, *args, **kwds) -> Dict:
        flow_send, flow_recv = await self.__get_flow()
        tcp_id, future = flow_recv.prepare_id_future(self.__api_delay * 2)
        await flow_send.send(tcp_id, path, *args, **kwds)
        try:
            return await asyncio.wait_for(future, self.__api_delay)
        except asyncio.TimeoutError:
            raise ServiceTimeoutError(f'服务调用超时:{self.__conn.host}:{self.__conn.port}:{path}:{args}:{kwds}')

    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        await self.close()
    pass


class TcpClientManage:
    @classmethod
    @MapKey(lambda _, *args: ':'.join((str(arg) for arg in args)))
    def __get_client(cls, host: str, port: int, api_delay: int, conn_timeout_base: int) -> TcpClient:
        return TcpClient(host, port, api_delay / 1000, conn_timeout_base / 1000)

    def __new__(cls, host: str, port: int, api_delay: float = 2, conn_timeout_base: float = 1) -> TcpClient:
        return cls.__get_client(host, port, int(api_delay * 1000), int(conn_timeout_base * 1000))

    @staticmethod
    async def create(tag: str, api_delay: float = 2, conn_timeout_base: float = 1) -> TcpClient:  # pragma: no cover
        host, port = await asyncio.gather(
            get_value_by_tag_and_field(tag, 'host'),
            get_value_by_tag_and_field(tag, 'port'),
        )
        return TcpClientManage(host, int(port), api_delay, conn_timeout_base)
    pass
