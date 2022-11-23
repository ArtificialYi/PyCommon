

from typing import Dict, List


class DictTool:
    @staticmethod
    def keys_omit(data: Dict, keys: List):
        """
        1. 返回True: 存在错误-（不是字典 or 字典错误）
        2. 返回False：格式正确-（是字典 and 所有key存在）
        """
        return not isinstance(data, dict) or any(
            data.get(key, None) is None
            for key in keys
        )
    pass
