from asyncio import StreamReader, StreamWriter
import json
from typing import Any, Callable, Optional

from ..tool.log_tool import Logger
from ..exception.tcp import ConnException
from .tcp import JsonOnline
from ..tool.server_tool import ServerRegister
from ..tool.loop_tool import NormLoop, OrderApi, TaskApi
from ..tool.bytes_tool import CODING


class FlowSendServer(OrderApi):
    """基于异步API流的TCP发送流-服务端版
    """
    def __init__(self, writer: StreamWriter, callback: Callable) -> None:
        self.__writer = writer
        OrderApi.__init__(self, self.send, callback)
        pass

    async def send(self, id: Optional[int], data: Any):
        str_json = json.dumps({
            'id': id,
            'data': data,
        })
        self.__writer.write(f'{str_json}\r\n'.encode(CODING))
        await self.__writer.drain()
        pass
    pass


class FlowJsonDeal(TaskApi):
    """服务端的Json处理流
    """
    def __init__(self, flow_send: FlowSendServer, callback: Callable, timeout: float = 1):
        self.__flow_send = flow_send
        TaskApi.__init__(self, self.deal_json, callback, timeout)
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id')
        service_name = json_obj.get('service')
        args = json_obj.get("args", [])
        kwds = json_obj.get("kwds", {})
        await Logger.info(f'已接收数据:{id}|{service_name}|{args}|{kwds}')
        res_service = await ServerRegister.call(service_name, *args, **kwds)
        await Logger.info(f'返回结果:{id}|{res_service}')
        await self.__flow_send.send(id, res_service)
        pass
    pass


class FlowRecv(NormLoop):
    """持续运行的TCP接收流
    """
    def __init__(
        self, reader: StreamReader,
        json_deal: FlowJsonDeal,
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
            raise ConnException('客户端断开连接')

        str_tmp = data.decode(CODING)
        for json_obj in self.__json_online.append(str_tmp):
            # 将json数据发送给其他流处理
            print(f'已接收数据:{json_obj}')
            await self.__json_deal.deal_json(json_obj)
        pass
    pass
