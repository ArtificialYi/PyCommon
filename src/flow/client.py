from asyncio import StreamWriter
import asyncio
from typing import Union

from .base import ActionJsonDeal

from ..tool.map_tool import Map

from ..tool.bytes_tool import CODING
from ..machine.mode import DeadWaitFlow
import json


class FlowSendClient(DeadWaitFlow):
    """基于异步API流的TCP发送流-客户端版
    """
    def __init__(self, writer: StreamWriter) -> None:
        self.__writer = writer
        super().__init__(self.send)
        pass

    async def send(self, id: int, server_name: str, *args, **kwds):
        str_json = json.dumps({
            'id': id,
            'server_name': server_name,
            'args': args,
            'kwds': kwds,
        })
        self.__writer.write(f'{str_json}\r\n'.encode(CODING))
        await self.__writer.drain()
        pass
    pass


class FlowJsonDealForClient(DeadWaitFlow, ActionJsonDeal):
    """客户端的Json处理流
    """
    def __init__(self, map: Map):
        self.__map = map
        DeadWaitFlow.__init__(self, self.deal_json)
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id', None)
        if id is None:
            raise Exception(f'Json数据错误:{json_obj}')
        future: Union[asyncio.Future, None] = self.__map.get_norm_value(id, None)
        if future is None:
            raise Exception(f'未找到对应的future:{id}')
        # 将data结果写入future（超时限制）
        future.set_result(json_obj.get('data', None))
        pass
    pass
