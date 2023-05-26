from functools import wraps
from typing import Callable

import pytest


class PytestAsyncTimeout:
    def __init__(self, t: int) -> None:
        self.__time = t
        # self.__delay = 0
        pass

    def __call__(self, func: Callable):
        @pytest.mark.timeout(self.__time)
        @pytest.mark.asyncio
        @wraps(func)
        async def func_pytest(*args, **kwds):
            return await func(*args, **kwds)
        return func_pytest
    pass
