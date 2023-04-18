import asyncio
from enum import Enum, auto
import itertools
from typing import Any, Callable, Dict, Union

from ..tool.func_tool import FqsSync


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
    def __init__(self, func: Union[Callable, None], weight=float('inf'), count=0) -> None:
        self.__weight = weight
        self.__func = func
        self.__count = count
        pass

    @property
    def weight(self):
        return self.__weight

    @property
    def func(self) -> Union[Callable, None]:
        return self.__func

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
    def num_edge(self):
        return len(self.__value_dict)

    def __gragh_init(self):
        self.__gragh_key_init()
        self.__gragh_value_init()

        for edge, value in self.__value_dict.items():
            self.__status_graph[edge.start][edge.end] = value
            pass
        pass

    def __gragh_key_init(self):
        for i in self.__node_set:
            self.__status_graph[i] = dict()
            pass
        pass

    def __gragh_value_init(self):
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
        self.__gragh_init()
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
            self.__status_graph[i][j] = StatusValue(self.__status_graph[i][k].func, weight_tmp, count_tmp)
            pass
        pass

    def get(self, start, end) -> Union[StatusValue, None]:
        dict_value = self.__status_graph.get(start, None)
        return dict_value.get(end, None) if dict_value is not None else None
    pass


class SGForFlow:
    """供给流使用的双状态状态图
    1. 拥有状态图本身
    2. 拥有状态图当前状态
    """
    class State(Enum):
        STARTED = auto()
        EXITED = auto()
        pass

    def __init__(self, func_starting: Callable, status: State = State.EXITED) -> None:
        self.__graph = self.__build(func_starting)
        self.__status = status
        pass

    def __build(self, func_starting: Callable):
        graph = StatusGraph()
        graph.add(
            StatusEdge(self.__class__.State.EXITED, self.__class__.State.STARTED),
            StatusValue(self.__start)
        )
        graph.add(
            StatusEdge(self.__class__.State.STARTED, self.__class__.State.STARTED),
            StatusValue(func_starting)
        )
        graph.add(
            StatusEdge(self.__class__.State.STARTED, self.__class__.State.EXITED),
            StatusValue(self.__exit)
        )
        graph.build(0)
        return graph

    def __start(self):
        self.__status = self.__class__.State.STARTED
        return self.__status

    def __exit(self):
        self.__status = self.__class__.State.EXITED
        return self.__status

    @property
    def status(self):
        return self.__status

    @property
    def graph(self):
        return self.__graph
    pass


class SGMachineForFlow(FqsSync):
    """有限状态机下的状态图
    1. 拥有状态图的状态转移函数-每个状态图都有
    2. 拥有状态图的当前状态-每个状态图都有
    3. 拥有状态图的退出状态-特殊的状态图才有
    4. 获取状态图当前状态下的函数-每个状态图都有
    """
    def __init__(self, graph: SGForFlow) -> None:
        """状态机的初始可以是任意状态
        1. 所有状态转化应该由自身控制
        2. 状态转化权最好仅由管理员拥有
        """
        self.__graph = graph
        super().__init__(self.__status_change)
        self.__status_exited = graph.State.EXITED
        pass

    @property
    def status(self):
        return self.__graph.status

    @property
    def status_exited(self):
        return self.__status_exited

    def func_get(self) -> Union[Callable, None]:
        value = self.__graph.graph.get(self.__graph.status, self.__graph.status)
        return value.func if value is not None else None

    async def __status_change(self, status_target, *args, **kwds):
        # 所有状态转移均在此处处理
        value = self.__graph.graph.get(self.__graph.status, status_target)
        func = value.func if value is not None else None
        if func is None:
            return None
        res = func(*args, **kwds)
        return await res if asyncio.iscoroutinefunction(func) else res

    async def __aenter__(self):
        await self.__status_change(self.__graph.State.STARTED)
        return await super().__aenter__()

    async def __aexit__(self, *args):
        res = await super().__aexit__(*args)
        await self.__status_change(self.__graph.State.EXITED)
        return res
    pass
