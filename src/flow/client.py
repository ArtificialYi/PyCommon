from asyncio import StreamReader, StreamWriter
import asyncio
from typing import Any

from ..tool.base import AsyncBase

from ...configuration.log import LoggerLocal

from ..exception.tcp import ConnException
from .tcp import JsonOnline
from ..tool.loop_tool import NormLoop, OrderApi
from ..tool.bytes_tool import CODING
import json


class FlowSendClient(OrderApi):
    """基于异步API流的TCP发送流-客户端版
    """
    def __init__(self, writer: StreamWriter) -> None:
        self.__writer = writer
        super().__init__(self.send)
        pass

    async def send(self, id: int, service: str, *args, **kwds):
        str_json = json.dumps({
            'id': id,
            'service': service,
            'args': args,
            'kwds': kwds,
        })
        self.__writer.write(f'{str_json}\r\n'.encode(CODING))
        await self.__writer.drain()
        pass
    pass


class JsonDeal:
    """客户端的Json处理流
    """
    def __init__(self) -> None:
        self.__map_future = dict[int, asyncio.Future[Any]]()
        pass

    def future_hook(self, id: int, future: asyncio.Future, timeout: float):
        self.__map_future[id] = future
        AsyncBase.call_later(timeout, self.__map_future.pop, id, None)
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id')
        if id is None:  # pragma: no cover
            await LoggerLocal.warning(f'客户端：未接收到id:{json_obj}')
            return

        future = self.__map_future.pop(id, None)
        if future is None:  # pragma: no cover
            await LoggerLocal.error(f'客户端：未找到对应的future:{json_obj}')
            return
        # 将data结果写入future（超时限制）
        future.set_result(json_obj.get('data'))
        pass
    pass


class FlowRecv(NormLoop):
    """持续运行的TCP接收流
    """
    def __init__(self, reader: StreamReader) -> None:
        self.__reader = reader
        NormLoop.__init__(self, self.__recv)
        self.__json_online = JsonOnline()
        self.__json_deal = JsonDeal()
        self.__tcp_id = 0
        pass

    def prepare_id_future(self, timeout: float):
        self.__tcp_id += 1
        future = AsyncBase.get_future()
        self.__json_deal.future_hook(self.__tcp_id, future, timeout)
        return self.__tcp_id, future

    async def __recv(self):
        data = await self.__reader.read(1)
        if not data:
            raise ConnException('服务端断开连接')

        str_tmp = data.decode(CODING)
        for json_obj in self.__json_online.append(str_tmp):
            # 将json数据发送给其他流处理
            await LoggerLocal.info(f'客户端：已接收数据:{json_obj}')
            await self.__json_deal.deal_json(json_obj)
        pass
    pass
