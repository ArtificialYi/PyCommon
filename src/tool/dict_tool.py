

from typing import Dict, List


class DictTool:
    @staticmethod
    def keys_exists(data: Dict, keys: List):
        """
        1. 返回True: 存在错误-（不是字典 or 字典错误）
        2. 返回False：格式正确-（是字典 and 所有key存在）
        """
        return isinstance(data, dict) and all(
            data.get(key, None) is not None
            for key in keys
        )
    pass
