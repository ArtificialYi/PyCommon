from asyncio import StreamReader
import json
from typing import Callable, Generator, Union

from .client import FlowJsonDealForClient

from .server import FlowJsonDealForServer

from ..tool.loop_tool import NormLoop

from ..tool.bytes_tool import CODING


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

        json_data = json.loads(self.__cache[:self.__idx + 1])
        self.__cache = self.__cache[self.__idx + 1:]
        self.__idx = 0
        return json_data
    pass


class FlowRecv(NormLoop):
    """持续运行的TCP接收流
    """
    def __init__(
        self, reader: StreamReader,
        json_deal: Union[FlowJsonDealForServer, FlowJsonDealForClient],
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
            raise Exception('连接已断开')

        str_tmp = data.decode(CODING)
        print('已接收数据:', str_tmp)
        for json_obj in self.__json_online.append(str_tmp):
            # 将json数据发送给其他流处理
            print(f'已接收数据:{json_obj}')
            await self.__json_deal.deal_json(json_obj)
        pass
    pass
