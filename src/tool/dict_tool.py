import asyncio
from contextlib import contextmanager
from typing import Any, Iterable


class KeyNotExistError(Exception):
    pass


class DictTool:
    @staticmethod
    def assert_key_exist(data: dict, key):
        if data.get(key) is None:
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
    def get_value_dict(data: dict, key):
        if key not in data:
            data[key] = dict()
            pass
        return data[key]
    pass


class LoopDict(dict):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__loop = None
        pass

    def __loop_init(self):
        loop = asyncio.get_event_loop()
        if self.__loop != loop:
            self.clear()
            self.__loop = loop
            pass

    def __getitem__(self, __key: Any) -> Any:
        self.__loop_init()
        return super().__getitem__(__key)

    def __setitem__(self, __key: Any, __value: Any) -> None:
        self.__loop_init()
        return super().__setitem__(__key, __value)
    pass
