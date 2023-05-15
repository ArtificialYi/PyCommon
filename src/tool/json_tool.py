import json
from typing import Any


class HyJsonEncoder(json.JSONEncoder):
    def default(self, o: BaseException) -> Any:
        return {
            'type': type(o).__name__,
            'args': o.args,
        }
    pass
