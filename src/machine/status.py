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


class NormStatusGraph:
    """普通的状态图
    """
    class State(Enum):
        STARTED = auto()
        STOPPED = auto()
        EXITED = auto()
        pass

    def __init__(self, func_starting: Callable, status: State = State.STARTED) -> None:
        """状态机的初始可以是任意状态
        1. 所有状态转化应该由自身控制
        2. 状态转化权最好仅由管理员拥有
        """
        self.__graph = self.__graph_build(func_starting)
        self.__status = status
        self.__status_exited = self.__class__.State.EXITED
        pass

    @property
    def status(self):
        return self.__status

    @property
    def status_exited(self):
        return self.__status_exited

    def func_get(self) -> Union[Callable, None]:
        value = self.__graph.get(self.__status, self.__status)
        return value.func if value is not None else None

    def func_get_target(self, status: State) -> Union[Callable, None]:
        value = self.__graph.get(self.__status, status)
        return value.func if value is not None else None

    def __status2target(self, status: State) -> bool:
        if self.__graph.get(self.__status, status) is None:
            return False
        self.__status = status
        return True

    def __graph_build(self, func_starting: Callable):
        graph_tmp = StatusGraph()
        graph_tmp.add(
            StatusEdge(self.__class__.State.STOPPED, self.__class__.State.STARTED),
            StatusValue(self.__start)
        )
        graph_tmp.add(
            StatusEdge(self.__class__.State.STARTED, self.__class__.State.STARTED),
            StatusValue(func_starting)
        )
        graph_tmp.add(
            StatusEdge(self.__class__.State.STARTED, self.__class__.State.STOPPED),
            StatusValue(self.__stop)
        )
        graph_tmp.add(
            StatusEdge(self.__class__.State.STOPPED, self.__class__.State.EXITED),
            StatusValue(self.__exit)
        )
        graph_tmp.add(
            StatusEdge(self.__class__.State.STARTED, self.__class__.State.EXITED),
            StatusValue(self.__exit)
        )
        graph_tmp.build(0)
        return graph_tmp

    def __start(self):
        return self.__status2target(self.__class__.State.STARTED)

    def __stop(self):
        return self.__status2target(self.__class__.State.STOPPED)

    def __exit(self):
        return self.__status2target(self.__class__.State.EXITED)
    pass
