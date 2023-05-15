from asyncio import StreamReader, StreamWriter
import asyncio
from typing import Dict

from ...configuration.log import LoggerLocal

from ..tool.base import AsyncBase
from ..exception.tcp import ConnException
from .tcp import JsonOnline
from ..tool.loop_tool import NormLoop, OrderApiSync
from ..tool.bytes_tool import CODING
import json


class FlowSendClient(OrderApiSync):
    """基于异步API流的TCP发送流-客户端版
    """
    def __init__(self, writer: StreamWriter, delay: float = 4) -> None:
        self.__writer = writer
        OrderApiSync.__init__(self, self.send)
        self.__future_map: Dict[int, asyncio.Future] = dict()
        self.__delay = delay
        pass

    def __map_del(self, id: int):
        self.__future_map.pop(id, None)

    @property
    def future_map(self):
        return self.__future_map

    async def send(self, id: int, service: str, *args, **kwds):
        str_json = json.dumps({
            'id': id,
            'service': service,
            'args': args,
            'kwds': kwds,
        })
        self.__writer.write(f'{str_json}\r\n'.encode(CODING))
        future = AsyncBase.get_future()
        self.__future_map[id] = future
        await self.__writer.drain()
        AsyncBase.call_later(self.__delay, self.__map_del, id)
        return future
    pass


class JsonDeal:
    """客户端的Json处理流
    """
    def __init__(self, map: Dict[int, asyncio.Future]) -> None:
        self.__map = map
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id')
        if id is None:
            await LoggerLocal.warning(f'客户端：未接收到id:{json_obj}')
            return

        future = self.__map.pop(id, None)
        if future is None:
            await LoggerLocal.error(f'客户端：未找到对应的future:{json_obj}')
            return
        # 将data结果写入future（超时限制）
        future.set_result(json_obj.get('data'))
        pass
    pass


class FlowRecv(NormLoop):
    """持续运行的TCP接收流
    """
    def __init__(self, reader: StreamReader, json_deal: JsonDeal,) -> None:
        self.__reader = reader
        NormLoop.__init__(self, self.__recv)
        self.__json_online = JsonOnline()
        self.__json_deal = json_deal
        pass

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
