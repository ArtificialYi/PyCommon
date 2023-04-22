from asyncio import StreamWriter
import asyncio
import json
from typing import Any, Callable, Dict, Tuple, Union

from ..tool.loop_tool import OrderApi

from ..tool.bytes_tool import CODING


class ServerRegister:
    __TABLE: Dict[str, Tuple[Callable, bool]] = dict()

    def __init__(self, path: Union[str, None] = None):
        self.__path = path
        pass

    def __call__(self, func: Callable):
        path = f'{ "" if self.__path is None else self.__path}/{func.__name__}'
        if self.__class__.__TABLE.get(path, None) is not None:
            raise Exception(f'服务已存在:{path}')
        self.__class__.__TABLE[path] = func, asyncio.iscoroutinefunction(func)
        return func

    @classmethod
    async def call(cls, path, *args, **kwds) -> Tuple[Callable, bool]:
        if cls.__TABLE.get(path, None) is None:
            raise Exception(f'服务不存在:{path}')
        func, is_async = cls.__TABLE[path]
        func_res = func(*args, **kwds)
        return await func_res if is_async else func_res
    pass


class FlowSendServer(OrderApi):
    """基于异步API流的TCP发送流-服务端版
    """
    def __init__(self, writer: StreamWriter, callback: Callable) -> None:
        self.__writer = writer
        OrderApi.__init__(self, self.send, callback)
        pass

    async def send(self, id: Union[int, None], data: Any):
        str_json = json.dumps({
            'id': id,
            'data': data,
        })
        self.__writer.write(f'{str_json}\r\n'.encode(CODING))
        await self.__writer.drain()
        pass
    pass


class ServiceMapping:
    """服务映射（异步无序-有超时）
    1. 从注册表中获取服务
    2. 使用返回值调用服务推送流
    """
    async def __call__(self, id: Union[int, None], service_name: Union[str, None], *args, **kwds):
        try:
            return await asyncio.wait_for(ServerRegister.call(service_name, *args, **kwds), 1)
        except asyncio.TimeoutError:
            raise Exception(f'调用服务超时:{id}|{service_name}|{args}|{kwds}')
        pass
    pass


class FlowJsonDealForServer(OrderApi):
    """服务端的Json处理流
    """
    def __init__(self, flow_send: FlowSendServer, callback: Callable):
        self.__flow_send = flow_send
        self.__service_mapping = ServiceMapping()
        OrderApi.__init__(self, self.deal_json, callback)
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id')
        service_name = json_obj.get('service')
        args = json_obj.get("args", [])
        kwds = json_obj.get("kwds", {})
        print(f'已接收数据:{id}|{service_name}|{args}|{kwds}')
        res_service = await self.__service_mapping(id, service_name, *args, **kwds)
        print(f'返回结果:{id}|{res_service}')
        await self.__flow_send.send(id, res_service)
        pass
    pass
