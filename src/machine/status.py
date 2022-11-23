
import itertools
from typing import Any, Dict, Union


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
    def __init__(self, weight, coro, count=0) -> None:
        self.__weight = weight
        self.__coro = coro
        self.__count = count
        pass

    @property
    def weight(self):
        return self.__weight

    @property
    def coro(self):
        return self.__coro

    @property
    def count(self):
        return self.__count
    pass


class StatusGragh(object):
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
        self.__gragh_dict: Dict[Any, Dict[Any, StatusValue]] = dict()
        pass

    @property
    def status_gragh(self):
        return self.__gragh_dict

    @property
    def value_dict(self):
        return self.__value_dict

    def _gragh_init(self):
        self._gragh_key_init()
        self._gragh_value_init()

        for edge, value in self.value_dict.items():
            self.status_gragh[edge.start][edge.end] = value
            pass
        pass

    def _gragh_key_init(self):
        for i in self.__node_set:
            self.status_gragh[i] = dict()
            pass
        pass

    def _gragh_value_init(self):
        max_tmp = StatusValue(float('inf'), None)
        for i, j in itertools.permutations(self.__node_set, 2):
            self.status_gragh[i][j] = max_tmp
            pass
        pass

    def add(self, edge: StatusEdge, value: StatusValue):
        if edge.start == edge.end:
            raise Exception("自身不连接自身")

        self.__node_set.add(edge.start)
        self.__node_set.add(edge.end)

        value_tmp = self.value_dict.get(edge, None)
        if value_tmp is None or value.weight < value_tmp.weight:
            self.value_dict[edge] = value
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
            weight_tmp = self.status_gragh[i][k].weight + self.status_gragh[k][j].weight
            count_tmp = self.status_gragh[i][k].count + self.status_gragh[k][j].count + 1
            if count_tmp > count_max or weight_tmp >= self.status_gragh[i][j].weight:
                continue
            self.status_gragh[i][j] = StatusValue(weight_tmp, self.status_gragh[i][k].coro, count_tmp)
            pass
        pass

    def get(self, start, end) -> Union[StatusValue, None]:
        return self.status_gragh[start].get(end, None)
    pass
