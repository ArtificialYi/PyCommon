from asyncio import StreamReader, StreamWriter
import asyncio
from typing import Callable, Dict

from ..exception.tcp import ConnException, FutureException, JsonIdException

from .tcp import JsonOnline

from ..tool.loop_tool import NormLoop, OrderApi

from ..tool.bytes_tool import CODING
import json


class FlowSendClient(OrderApi):
    """基于异步API流的TCP发送流-客户端版
    """
    def __init__(self, writer: StreamWriter, callback: Callable) -> None:
        self.__writer = writer
        OrderApi.__init__(self, self.send, callback)
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
    def __init__(self, map: Dict[int, asyncio.Future]) -> None:
        self.__map = map
        pass

    def deal_json(self, json_obj: dict):
        id = json_obj.get('id', None)
        if id is None:  # pragma: no cover
            raise JsonIdException(f'Json数据错误:{json_obj}')
        future = self.__map.get(id, None)
        if future is None:  # pragma: no cover
            raise FutureException(f'未找到对应的future:{id}')
        # 将data结果写入future（超时限制）
        future.set_result(json_obj.get('data', None))
        pass
    pass


class FlowRecv(NormLoop):
    """持续运行的TCP接收流
    """
    def __init__(
        self, reader: StreamReader,
        json_deal: JsonDeal,
        callback: Callable,
    ) -> None:
        self.__reader = reader
        NormLoop.__init__(self, self.__recv, callback)
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
            print(f'已接收数据:{json_obj}')
            self.__json_deal.deal_json(json_obj)
        pass
    pass
