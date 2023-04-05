from abc import abstractmethod
from asyncio import StreamReader, StreamWriter
import asyncio
import inspect
from typing import Any, Callable, Dict, Generator, Tuple, Union

from ..tool.map_tool import Map

from ..tool.bytes_tool import CODING
from ..machine.mode import DeadWaitFlow, NormFlow
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


class JsonOnline:
    def __init__(self) -> None:
        self.__cache = ''
        self.__idx = 0
        pass

    def append(self, data: str) -> Generator[dict, None, None]:
        self.__cache += data
        while self.__idx < len(self.__cache) - 1:
            json_obj = self.__step()
            if json_obj is None:
                continue
            yield json_obj
        pass

    def __step(self) -> Union[dict, None]:
        pos = self.__cache[self.__idx:].find('\r\n')
        self.__idx = self.__idx + pos + 1 if pos != -1 else len(self.__cache) - 1
        if pos == -1:
            return None
        return self.__str2json(self.__cache[:self.__idx + 1])

    def __str2json(self, str_json: str) -> Union[dict, None]:
        try:
            json_data = json.loads(str_json)
            self.__cache = self.__cache[self.__idx + 1:]
            self.__idx = 0
            return json_data
        except json.JSONDecodeError:
            return None
    pass


class ActionJsonDeal:
    @abstractmethod
    async def deal_json(cls, json_obj: dict):
        raise NotImplementedError
    pass


class FlowRecv(NormFlow):
    """持续运行的TCP接收流
    """
    def __init__(self, reader: StreamReader, json_deal: ActionJsonDeal) -> None:
        self.__reader = reader
        super().__init__(self.__recv)
        self.__json_online = JsonOnline()
        self.__json_deal = json_deal
        pass

    async def __recv(self):
        data = await self.__reader.read(1)
        if not data:
            raise Exception('连接已断开')

        str_tmp = data.decode(CODING)
        for json_obj in self.__json_online.append(str_tmp):
            # 将json数据发送给其他流处理
            print(f'已接收数据:{json_obj}')
            await self.__json_deal.deal_json(json_obj)
        pass
    pass


class FlowSendServer(DeadWaitFlow):
    """基于异步API流的TCP发送流-服务端版
    """
    def __init__(self, writer: StreamWriter) -> None:
        self.__writer = writer
        super().__init__(self.send)
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


class ServerRegister:
    __TABLE: Dict[str, Tuple[Callable, bool]] = dict()

    def __init__(self, path: Union[str, None] = None):
        self.__path = path
        pass

    def __call__(self, func: Callable):
        path = f'{ "" if self.__path is None else self.__path}/{func.__name__}'
        if self.__class__.__TABLE.get(path, None) is not None:
            raise Exception(f'服务已存在:{path}')
        self.__class__.__TABLE[path] = func, inspect.isasyncfunction(func)
        return func

    @classmethod
    async def call(cls, path: str, *args, **kwds) -> Tuple[Callable, bool]:
        if cls.__TABLE.get(path, None) is None:
            raise Exception(f'服务不存在:{path}')
        func, is_async = cls.__TABLE[path]
        func_res = func(*args, **kwds)
        return await func_res if is_async else func_res
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
        res = await ServerRegister.call(service_name, *args, **kwds)
        await self.__send.send(id, res)
        pass

    async def __timeout_service(self, timeout: int, id: int, service_name: str, *args, **kwds):
        try:
            return await asyncio.wait_for(self.__service_mapping(id, service_name, *args, **kwds), timeout)
        except asyncio.TimeoutError:
            raise Exception(f'调用服务超时:{id}|{service_name}|{args}|{kwds}')
        pass

    async def __call__(self, id: int, service_name: str, *args, **kwds):
        res = await self.__timeout_service(5, id, service_name, *args, **kwds)
        await self.__send.send(id, res)
        pass
    pass


class FlowJsonDealForServer(DeadWaitFlow, ActionJsonDeal):
    """服务端的Json处理流
    """
    def __init__(self, flow_send: FlowSendServer):
        self.__service_mapping = ServiceMapping(flow_send)
        DeadWaitFlow.__init__(self, self.deal_json)
        pass

    async def deal_json(self, json_obj: dict):
        id = json_obj.get('id', None)
        service_name = json_obj.get('server_name', None)
        if id is None or service_name is None:
            raise Exception(f'Json数据错误:{json_obj}')
        await self.__service_mapping(id, service_name, *json_obj.get('args', []), **json_obj.get('kwds', {}))
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
