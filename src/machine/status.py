from enum import Enum, auto
import itertools
from typing import Any, Callable, Dict, Union


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
            self.__status_graph[i][j] = StatusValue(self.__status_graph[i][k].func, weight_tmp, count_tmp)
            pass
        pass

    def get(self, start, end) -> Union[StatusValue, None]:
        return self.__status_graph[start].get(end, None)
    pass


class StatusGraphBase:
    def __init__(self) -> None:
        self._status = None
        self.__status_graph: StatusGraph = self._graph_build()
        pass

    def status2target(self, status):
        self._status = status
        pass

    def _graph_build(self) -> StatusGraph:
        """
        状态转移方程式
        需要子类重写
        """
        raise Exception('子类需要重写这个函数')

    def func_get(self) -> Union[Callable, None]:
        value = self.__status_graph.get(self._status, self._status)
        return value.func if value is not None else None

    def func_get_target(self, status) -> Union[Callable, None]:
        value = self.__status_graph. get(self._status, status)
        return value.func if value is not None else None
    pass


class NormStatusGraph(StatusGraphBase):
    """普通的状态图
    """
    class State(Enum):
        STARTED = auto()
        STOPPED = auto()
        EXITED = auto()
        pass

    def __init__(self) -> None:
        """状态机的初始应该是EXITED状态
        1. 从EXITED状态到其他状态应该由loop管理者控制(因为EXITED状态会退出loop)
        2. 其他状态之间的变化由状态机控制
        """
        StatusGraphBase.__init__(self)
        self.status2target(NormStatusGraph.State.EXITED)
        pass

    def _graph_build(self):
        graph_tmp = StatusGraph()
        graph_tmp.add(
            StatusEdge(NormStatusGraph.State.STOPPED, NormStatusGraph.State.STARTED),
            StatusValue(self.__start)
        )
        graph_tmp.add(
            StatusEdge(NormStatusGraph.State.STARTED, NormStatusGraph.State.STARTED),
            StatusValue(self._starting)
        )
        graph_tmp.add(
            StatusEdge(NormStatusGraph.State.STARTED, NormStatusGraph.State.STOPPED),
            StatusValue(self.__stop)
        )
        graph_tmp.add(
            StatusEdge(NormStatusGraph.State.STOPPED, NormStatusGraph.State.EXITED),
            StatusValue(self.__exit)
        )
        graph_tmp.build(0)
        return graph_tmp

    async def __start(self):
        self.status2target(self.__class__.State.STARTED)

    async def __stop(self):
        self.status2target(self.__class__.State.STOPPED)

    async def __exit(self):
        self.status2target(self.__class__.State.EXITED)

    async def _starting(self):
        """
        启动中状态运行函数(子类需要重写这个函数)
        """
        raise Exception('子类需要重写这个函数')
    pass
