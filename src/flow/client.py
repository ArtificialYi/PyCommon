from asyncio import StreamReader, StreamWriter
from typing import Generator, Union

from ..tool.bytes_tool import CODING
from ..machine.mode import DeadWaitFlow, NormFlow
import json


class FlowSend(DeadWaitFlow):
    """基于异步API流的TCP发送流-客户端版
    """
    def __init__(self, writer: StreamWriter) -> None:
        self.__writer = writer
        super().__init__(self.__send)
        pass

    async def __send(self, id: int, server_name: str, *args, **kwds):
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


class FlowRecv(NormFlow):
    """持续运行的TCP接收流
    """
    def __init__(self, reader: StreamReader) -> None:
        self.__reader = reader
        super().__init__(self.__recv)
        self.__json_online = JsonOnline()
        pass

    async def __recv(self):
        data = await self.__reader.read(1)
        if not data:
            raise Exception('连接已断开')

        str_tmp = data.decode(CODING)
        for json_obj in self.__json_online.append(str_tmp):
            # 将json数据发送给其他流处理
            print(f'已接收数据:{json_obj}')
        pass
    pass
