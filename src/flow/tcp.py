import json
from typing import Generator, Union


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
