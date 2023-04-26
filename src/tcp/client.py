import asyncio
from typing import Tuple

from ..tool.async_tool import AsyncTool

from ..tool.map_tool import LockManage, MapKey

from ..tool.base import AsyncBase
from ..tool.func_tool import FuncTool, QueueException
from ..flow.client import JsonDeal, FlowSendClient, FlowRecv


class TcpApi:
    """TCP实际开放的API
    """
    def __init__(self, host: str, port: int) -> None:
        self.__host = host
        self.__port = port
        self.__task = AsyncBase.get_done_task()
        self.__lock = LockManage()
        pass

    async def __flow_run(self, future: asyncio.Future):
        reader, writer = await asyncio.open_connection(self.__host, self.__port)
        try:
            err_queue = QueueException()
            future_map = dict()
            deal = JsonDeal(future_map)
            async with (
                FlowSendClient(writer, err_queue) as flow_send,
                FlowRecv(reader, deal, err_queue),
            ):  # pragma: no cover
                future.set_result((flow_send, future_map))
                await err_queue.exception_loop(3)
        except BaseException as e:
            # TODO: 此处需记录每次断开连接的原因
            # print(e)
            raise e
        finally:
            writer.close()
            await writer.wait_closed()

    def __next_id(self):
        self.__tcp_id += 1
        return self.__tcp_id

    async def __get_flow_send(self) -> Tuple[FlowSendClient, int, dict, asyncio.Task]:
        async with self.__lock.get_lock():
            if self.__task.done():
                future: asyncio.Future[Tuple[FlowSendClient, dict]] = asyncio.Future()
                self.__task = AsyncBase.coro2task_exec(self.__flow_run(future))
                done, _ = await asyncio.wait([
                    self.__task, future
                ], return_when=asyncio.FIRST_COMPLETED)
                self.__flow_send, self.__future_map = done.pop().result()
                self.__tcp_id = 0
                pass
            pass
        tcp_id = self.__next_id()
        return self.__flow_send, tcp_id, self.__future_map, self.__task

    async def api(self, path: str, *args, **kwds):
        flow_send, tcp_id, future_map, task_main = await self.__get_flow_send()
        # 添加id映射
        future_map[tcp_id] = asyncio.Future()
        await flow_send.send(tcp_id, path, *args, **kwds)
        try:
            async with AsyncTool.coro_async_gen(asyncio.wait_for(future_map[tcp_id], 2)) as task:
                done, _ = await asyncio.wait([
                    task,
                    task_main,
                ], return_when=asyncio.FIRST_COMPLETED)
                return done.pop().result()
        finally:
            del future_map[tcp_id]

    async def close(self):
        task = self.__task
        task.cancel()
        await FuncTool.await_no_cancel(task)
        pass
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
