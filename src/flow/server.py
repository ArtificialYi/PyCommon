from asyncio import StreamReader, StreamWriter
import asyncio
import json
from typing import Any, Optional

from ..configuration.log import LoggerLocal

from ..tool.json_tool import HyJsonEncoder

from ..tool.loop_tool import NormLoop, OrderApi
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

    async def send(self, id: Optional[int], code: int, data: Any):
        str_json = json.dumps({
            'id': id,
            'type': type(data).__name__,
            'data': data,
        }, cls=HyJsonEncoder)
        self.__writer.write(f'{str_json}\r\n'.encode(CODING))
        await self.__writer.drain()
        pass
    pass


class JsonDeal:
    """服务端的Json处理流
    不会发生异常
    """
    def __init__(self, flow_send: FlowSendServer):
        self.__flow_send = flow_send
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id')
        service_name = json_obj.get('service')
        args = json_obj.get("args", [])
        kwds = json_obj.get("kwds", {})
        res_service = await ServerRegister.call(service_name, *args, **kwds)
        await self.__flow_send.send(id, 1 if isinstance(res_service, Exception) else 0, res_service)
        pass
    pass


class FlowRecvServer(NormLoop):
    """持续运行的TCP接收流
    只有客户端断开连接时会抛出异常，其他正常情况都不会
    """
    def __init__(
        self, reader: StreamReader,
        flow_send: FlowSendServer,
        timeout: float = 1,
    ) -> None:
        self.__reader = reader
        self.__json_online = JsonOnline()
        self.__json_deal = JsonDeal(flow_send)
        self.__timeout = timeout
        NormLoop.__init__(self, self.__recv)
        pass

    async def __recv(self):
        data = await self.__reader.read(1)
        if not data:
            raise ConnException('客户端断开连接')

        str_tmp = data.decode(CODING)
        for json_obj in self.__json_online.append(str_tmp):
            await LoggerLocal.info(f'服务端：已接收数据:{json_obj}')
            # 将json数据 异步处理
            asyncio.create_task(asyncio.wait_for(self.__json_deal.deal_json(json_obj), self.__timeout))
        pass
    pass
