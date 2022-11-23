import asyncio
from enum import Enum, auto
from typing import Any, Callable, Dict, Union

from ..tool.base import MatchCase


class State(Enum):
    STEP = auto()

    @staticmethod
    def update(tmp_dict: Dict[Any, Union[Callable, None]] = {}):
        tmp: Dict[Any, Union[Callable, None]] = {
            State.STEP: None,
        }
        tmp.update(tmp_dict)
        return tmp
    pass


class QueueMatchCase(MatchCase):
    def __init__(self, case_dict: Dict[Any, Union[Callable, None]], default: Union[Callable, None] = None) -> None:
        super().__init__(State.update(case_dict), default)
    pass


class QueueBase(asyncio.Queue):
    """对异步队列做了一层业务封装
    """
    async def put(self, state: Enum, *args, **kwds) -> None:
        return await super().put((state, args, kwds))
    pass


class StepQueue(QueueBase):
    """供给流内部使用的内部队列
    1. 附带空step
    """
    async def step(self):
        return await self.put(State.STEP)
    pass


class StepManage:
    def __init__(self) -> None:
        self.__q_step = StepQueue()
        pass

    @property
    def q_step(self):
        return self.__q_step
    pass


class QueueAction:
    """供给流外部使用的内部队列
    1. 自定义put(默认为Step)
    2. 附赠q_size
    """
    def __init__(self, q: QueueBase) -> None:
        self.__q = q
        pass

    async def put(self, *args, **kwds):
        return await self.__q.put(*args, **kwds)

    def qsize(self):
        return self.__q.qsize()

    async def join(self):
        return await self.__q.join()
    pass


class NormManageQueue(StepManage):
    def __init__(self, class_type: Callable) -> None:
        super().__init__()
        self.__q_action: QueueAction = class_type(self.q_step)
        pass

    @property
    def q_action(self):
        return self.__q_action
    pass
