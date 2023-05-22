from typing import Any, Dict


class KeyNotExistError(Exception):
    pass


class DictTool:
    @staticmethod
    def key_exist_raise(data: Dict, key: Any):
        if data.get(key) is None:
            raise KeyNotExistError(f'data: {data} key: {key} not exist')
    pass
