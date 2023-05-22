from typing import Iterable


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
    pass
