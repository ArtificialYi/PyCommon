
import asyncio
import itertools
from typing import Any, Callable, Dict, Union

from ...src.tool.base import AsyncBase


class FuncQueue:
    """将普通的函数包装成队列函数
    队列不为空时，会使用队列中的参数调用一次func_queue
    1. 默认当队列为空时，返回None
    2. 如果指定了func_default，那么当队列为空时，会调用func_default
    3. 如果指定了func_cond，那么当队列为空时，会判定func_cond为True时才会调用func_default
    """
    def __init__(
        self, func_default: Callable = lambda: None,
        func_queue: Callable = lambda: None, func_cond: Callable = lambda: True,
    ) -> None:
        self.__queue = asyncio.Queue()
        self.__func_cond = func_cond
        self.__is_coro_cond = asyncio.iscoroutinefunction(self.__func_cond)
        self.__func_queue = func_queue
        self.__is_coro_inner = asyncio.iscoroutinefunction(self.__func_queue)
        self.__func_default = func_default
        self.__is_coro_default = asyncio.iscoroutinefunction(self.__func_default)
        pass

    def __call__(self, *args, **kwds) -> asyncio.Task:
        """执行queue的内部流程
        """
        return AsyncBase.coro2task_exec(self.__inner(*args, **kwds))

    async def __cond(self):
        res = self.__func_cond()
        return await res if self.__is_coro_cond else res

    async def __inner(self, *args, **kwds):
        if self.__queue.qsize() == 0 and await self.__cond():
            return await self.__default()

        future, args, kwds = await self.__queue.get()
        res0 = self.__func_queue(*args, **kwds)
        res1 = await res0 if self.__is_coro_inner else res0
        future.set_result(res1)
        self.__queue.task_done()
        return res1

    async def __default(self):
        res = self.__func_default()
        return await res if self.__is_coro_default else res

    async def func(self, *args, **kwds):
        # queue的对外函数
        future = AsyncBase.get_future()
        await self.__queue.put((future, args, kwds))
        return await future
    pass


class StatusEdge(object):
    """
状态图中的边
    """
    def __init__(self, start, end) -> None:
        self.__start = start
        self.__end = end
        pass

    def __hash__(self) -> int:
        return hash((self.start, self.end))

    def __eq__(self, __o: object) -> bool:
        return isinstance(__o, StatusEdge) and (self.start == __o.start) and (self.end == __o.end)

    @property
    def start(self):
        return self.__start

    @property
    def end(self):
        return self.__end
    pass


class StatusValue(object):
    def __init__(self, func_queue: Union[FuncQueue, None], weight=float('inf'), count=0) -> None:
        self.__weight = weight
        self.__func_queue = func_queue
        self.__count = count
        pass

    @property
    def weight(self):
        return self.__weight

    @property
    def func_queue(self) -> Union[FuncQueue, None]:
        return self.__func_queue

    @property
    def count(self):
        return self.__count
    pass


class StatusGraph(object):
    """
状态图增删改查类
目标：
1. 提供根据当前状态和目标状态，返回最优边/None
过程：
1. 提供添加边节点能力
2. 提供构建图能力
    """
    def __init__(self) -> None:
        self.__node_set = set()
        self.__value_dict: Dict[StatusEdge, StatusValue] = dict()
        self.__status_graph: Dict[Any, Dict[Any, StatusValue]] = dict()
        pass

    @property
    def status_graph(self):
        return self.__status_graph

    @property
    def value_dict(self):
        return self.__value_dict

    @property
    def num_edge(self):
        return len(self.__value_dict)

    def _gragh_init(self):
        self._gragh_key_init()
        self._gragh_value_init()

        for edge, value in self.__value_dict.items():
            self.__status_graph[edge.start][edge.end] = value
            pass
        pass

    def _gragh_key_init(self):
        for i in self.__node_set:
            self.__status_graph[i] = dict()
            pass
        pass

    def _gragh_value_init(self):
        max_tmp = StatusValue(None)
        for i, j in itertools.permutations(self.__node_set, 2):
            self.__status_graph[i][j] = max_tmp
            pass
        pass

    def add(self, edge: StatusEdge, value: StatusValue):
        self.__node_set.add(edge.start)
        self.__node_set.add(edge.end)

        value_tmp = self.__value_dict.get(edge, None)
        if value_tmp is None or value.weight < value_tmp.weight:
            self.__value_dict[edge] = value
            pass
        pass

    def build(self, count_max: int = -1):
        """
        构建可以直接返回最优边的缓存
        floyd算法+自身不连接自身
        """
        self._gragh_init()
        count_max = len(self.__node_set) if count_max == -1 else count_max
        if count_max == 0:
            return None

        self.__gragh_build(count_max)
        pass

    def __gragh_build(self, count_max):
        for k, i, j in itertools.permutations(self.__node_set, 3):
            weight_tmp = self.__status_graph[i][k].weight + self.__status_graph[k][j].weight
            count_tmp = self.__status_graph[i][k].count + self.__status_graph[k][j].count + 1
            if count_tmp > count_max or weight_tmp >= self.__status_graph[i][j].weight:
                continue
            self.__status_graph[i][j] = StatusValue(self.__status_graph[i][k].func_queue, weight_tmp, count_tmp)
            pass
        pass

    def get(self, start, end) -> Union[StatusValue, None]:
        return self.__status_graph[start].get(end, None)
    pass
