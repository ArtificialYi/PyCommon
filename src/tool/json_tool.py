import json
from typing import Any


class HyJsonEncoder(json.JSONEncoder):
    def default(self, o: Any) -> Any:
        if isinstance(o, Exception):
            return {
                'type': type(o).__name__,
                'args': o.args,
            }
        return super().default(o)
    pass
