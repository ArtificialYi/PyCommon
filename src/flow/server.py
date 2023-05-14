from asyncio import StreamReader, StreamWriter
import json
from typing import Any, Optional

from ..tool.json_tool import HyJsonEncoder

from ..tool.loop_tool import NormLoop, OrderApi, TaskApi
from ..exception.tcp import ConnException
from .tcp import JsonOnline
from ..tool.server_tool import ServerRegister
from ..tool.bytes_tool import CODING


class FlowSendServer(OrderApi):
    """基于异步API流的TCP发送流-服务端版
    遇到任意异常均会结束
    """
    def __init__(self, writer: StreamWriter) -> None:
        self.__writer = writer
        OrderApi.__init__(self, self.send)
        pass

    async def send(self, id: Optional[int], data: Any):
        str_json = json.dumps({
            'id': id,
            'data': data,
        }, cls=HyJsonEncoder)
        self.__writer.write(f'{str_json}\r\n'.encode(CODING))
        await self.__writer.drain()
        pass
    pass


class FlowJsonDeal(TaskApi):
    """服务端的Json处理流
    不会发生异常
    """
    def __init__(self, flow_send: FlowSendServer, timeout: float = 1):
        self.__flow_send = flow_send
        TaskApi.__init__(self, self.deal_json, timeout=timeout)
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id')
        service_name = json_obj.get('service')
        args = json_obj.get("args", [])
        kwds = json_obj.get("kwds", {})
        res_service = await ServerRegister.call(service_name, *args, **kwds)
        await self.__flow_send.send(id, res_service)
        pass
    pass


class FlowRecv(NormLoop):
    """持续运行的TCP接收流
    只有客户端断开连接时会抛出异常，其他正常情况都不会
    """
    def __init__(
        self, reader: StreamReader,
        json_deal: FlowJsonDeal,
    ) -> None:
        self.__reader = reader
        self.__json_online = JsonOnline()
        self.__json_deal = json_deal
        NormLoop.__init__(self, self.__recv)
        pass

    async def __recv(self):
        data = await self.__reader.read(1)
        if not data:
            raise ConnException('客户端断开连接')

        str_tmp = data.decode(CODING)
        for json_obj in self.__json_online.append(str_tmp):
            # 将json数据发送给其他流处理
            print(f'已接收数据:{json_obj}')
            await self.__json_deal.deal_json(json_obj)
        pass
    pass
