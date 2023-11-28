import asyncio

from typing import Any, Iterable
from contextlib import contextmanager


class KeyNotExistError(Exception):
    pass


class LoopDict:
    def __init__(self):
        self.__dict = dict()
        self.__loop = None
        pass

    def __loop_init(self):
        loop = asyncio.get_event_loop()
        if self.__loop != loop:
            self.__dict.clear()
            self.__loop = loop
            pass

    def __contains__(self, __key: Any) -> bool:
        self.__loop_init()
        return __key in self.__dict

    def __getitem__(self, __key: Any) -> Any:
        self.__loop_init()
        return self.__dict[__key]

    def __setitem__(self, __key: Any, __value: Any) -> None:
        self.__loop_init()
        self.__dict[__key] = __value
        pass
    pass


class DictTool:
    @staticmethod
    def assert_key_exist(data: dict, key):
        if key not in data:
            raise KeyNotExistError(f'data: {data} key: {key} not exist')

    @staticmethod
    def assert_keys_exist(data: dict, keys: Iterable):
        for key in keys:
            DictTool.assert_key_exist(data, key)
            pass
        pass

    @staticmethod
    @contextmanager
    def swap_value(data: dict, key, value):
        tmp = data[key]
        data[key] = value
        yield data
        data[key] = tmp
        pass

    @staticmethod
    def get_loop(data: dict, key) -> LoopDict:
        if key not in data:
            data[key] = LoopDict()
            pass
        return data[key]
    pass
