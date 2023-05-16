import json
from typing import Any


class HyJsonEncoder(json.JSONEncoder):
    def default(self, o: BaseException) -> Any:
        return o.args[0]
    pass
