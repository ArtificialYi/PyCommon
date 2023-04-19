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
    async def call(cls, path: str, *args, **kwds) -> Tuple[Callable, bool]:
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

    async def send(self, id: int, data: Any):
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
    def __init__(self, flow_send: FlowSendServer):
        self.__send = flow_send
        pass

    async def __service_mapping(self, id: int, service_name: str, *args, **kwds):
        # 1. 从注册表中获取服务
        # 2. 使用返回值调用服务推送流
        print(f'尝试调用服务{id}|{service_name}|{args}|{kwds}')
        res = await ServerRegister.call(service_name, *args, **kwds)
        print(f'服务结果{id}|{res}')
        await self.__send.send(id, res)
        pass

    async def __timeout_service(self, timeout: float, id: int, service_name: str, *args, **kwds):
        try:
            return await asyncio.wait_for(self.__service_mapping(id, service_name, *args, **kwds), timeout)
        except asyncio.TimeoutError:
            raise Exception(f'调用服务超时:{id}|{service_name}|{args}|{kwds}')
        pass

    async def __call__(self, id: int, service_name: str, *args, **kwds):
        res = await self.__timeout_service(1, id, service_name, *args, **kwds)
        await self.__send.send(id, res)
        pass
    pass


class FlowJsonDealForServer(OrderApi):
    """服务端的Json处理流
    """
    def __init__(self, flow_send: FlowSendServer, callback: Callable):
        self.__service_mapping = ServiceMapping(flow_send)
        OrderApi.__init__(self, self.deal_json, callback)
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id', None)
        service_name = json_obj.get('service', None)
        print(f'已接收数据:{id}|{service_name}|{json_obj.get("args", [])}|{json_obj.get("kwds", {})}')
        if id is None or service_name is None:
            raise Exception(f'Json数据错误:{json_obj}')
        await self.__service_mapping(id, service_name, *json_obj.get('args', []), **json_obj.get('kwds', {}))
        pass
    pass
