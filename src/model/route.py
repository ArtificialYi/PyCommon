import heapq
import math
from typing import Dict, Optional


class ArgsLatitude:
    def __init__(self, length: int, layer: int, hidden: int):
        self.length = length
        self.layer = layer
        self.hidden = hidden
        pass

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ArgsLatitude):  # pragma: no cover
            raise TypeError("LayerHiddenLength 只可以与 LayerHiddenLength进行比较")
        return (self.length, self.layer, self.hidden) == (__value.length, __value.layer, __value.hidden)

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, ArgsLatitude):  # pragma: no cover
            raise TypeError("LayerHiddenLength 只可以与 LayerHiddenLength进行比较")
        return (self.length, self.layer, self.hidden) < (__value.length, __value.layer, __value.hidden)

    def __hash__(self) -> int:
        return hash((self.length, self.layer, self.hidden))

    def __next_length(self, length_max: int):
        length_next = self.length * 2
        if length_next > length_max:
            return None
        return ArgsLatitude(length_next, self.layer, self.hidden)

    def __pre_length(self, length_min: int):
        length_pre = self.length // 2
        if length_pre < length_min:
            return None
        return ArgsLatitude(length_pre, self.layer, self.hidden)

    def __next_layer(self, layer_max: int):
        layer_next = self.layer + 1
        if layer_next > layer_max or 2 ** layer_next > self.hidden:
            return None
        return ArgsLatitude(self.length, layer_next, self.hidden)

    def __pre_layer(self, layer_min: int):
        layer_pre = self.layer - 1
        if layer_pre < layer_min:
            return None
        return ArgsLatitude(self.length, layer_pre, self.hidden)

    def __next_hidden(self, hidden_max: int):
        hidden_next = self.hidden * 2
        if hidden_next > hidden_max:
            return None
        return ArgsLatitude(self.length, self.layer, hidden_next)

    def __pre_hidden(self, hidden_min: int):
        hidden_pre = self.hidden // 2
        if hidden_pre < hidden_min or hidden_pre < 2 ** self.layer:
            return None
        return ArgsLatitude(self.length, self.layer, hidden_pre)

    def next(self, length_max: int, layer_max: int, hidden_max: int):
        return [
            al for al in [
                self.__next_length(length_max),
                self.__next_layer(layer_max),
                self.__next_hidden(hidden_max),
            ] if al is not None
        ]

    def pre(self, length_min: int, layer_min: int, hidden_min: int):
        return [
            al for al in [
                self.__pre_length(length_min),
                self.__pre_layer(layer_min),
                self.__pre_hidden(hidden_min),
            ] if al is not None
        ]
    pass


class TrainUnit:
    def __init__(self, al: ArgsLatitude, loss_pre: float) -> None:
        self.al = al

        self.loss_pre = loss_pre
        self.loss_now = None
        pass

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, TrainUnit):  # pragma: no cover
            raise TypeError("TrainUnit 只可以与 TrainUnit进行比较")
        return math.isclose(self.loss_pre, __value.loss_pre, rel_tol=1e-4, abs_tol=1e-4) and self.al == __value.al

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, TrainUnit):  # pragma: no cover
            raise TypeError("TrainUnit 只可以与 TrainUnit进行比较")
        if math.isclose(self.loss_pre, __value.loss_pre, rel_tol=1e-4, abs_tol=1e-4):
            return self.al > __value.al
        return self.loss_pre > __value.loss_pre
    pass


class AlRoute:
    def __init__(self, length_max: int = 1, layer_max: int = 1, length_min: int = 1, layer_min: int = 1) -> None:
        # 待训练堆
        self.__heap = [TrainUnit(ArgsLatitude(1, 1, 2), float('inf'))]

        # 已训练字典
        self.__dict_trained = dict()

        # 参数范围
        self.__al_min = ArgsLatitude(length_min, layer_min, 2 ** layer_min)
        self.__al_max = ArgsLatitude(length_max, layer_max, 2 ** layer_max)
        pass

    def __pre_is_all_trained(self, al: ArgsLatitude) -> bool:
        for al_pre in al.pre(self.__al_min.length, self.__al_min.layer, self.__al_min.hidden):
            if self.__dict_trained.get(al_pre) is None:
                return False
            pass
        return True

    def can_push(self, al: ArgsLatitude) -> bool:
        # 节点在范围内 and 当前未训练 and (前置已训练 or 初始节点)
        return self.__al_min <= al <= self.__al_max and self.__dict_trained.get(al) is None and self.__pre_is_all_trained(al)

    def __iter_next(self, al: ArgsLatitude):
        for al_next in al.next(self.__al_max.length, self.__al_max.layer, self.__al_max.hidden):
            if self.__pre_is_all_trained(al_next):
                yield al_next
            pass
        pass

    def push(self, al: ArgsLatitude, loss: float) -> bool:
        # 过滤al
        if not self.can_push(al):
            return False

        # 已训练字典更新
        self.__dict_trained[al] = loss
        # 生成全新节点
        for al_next in self.__iter_next(al):
            heapq.heappush(self.__heap, TrainUnit(al_next, loss))
            pass
        return True

    def pop(self) -> Optional[TrainUnit]:
        if len(self.__heap) == 0:
            return None
        return heapq.heappop(self.__heap)
    pass


class UnitRoute:
    def __init__(self, length_max: int = 1, layer_max: int = 1, length_min: int = 1, layer_min: int = 1):
        key_tmp = ArgsLatitude(1, 1, 2)
        value_tmp = TrainUnit(key_tmp, float('inf'), float('inf'))

        # 待训练堆(以速度排序)
        self.__heap = [value_tmp]
        # 已训练集合
        self.__dict_trained: Dict[ArgsLatitude, TrainUnit] = dict()

        self.__length_max = length_max
        self.__layer_max = layer_max
        self.__hidden_max = 2 ** self.__layer_max

        self.__length_min = length_min
        self.__layer_min = layer_min
        self.__hidden_min = 2 ** self.__layer_min
        pass

    def refresh_node(self, speed_now: float, loss_now: float):
        tmp_next = self.get_next()
        eq_res = tmp_next is None or math.isclose(tmp_next.loss_pre, loss_now, rel_tol=1e-4, abs_tol=1e-4)
        if eq_res or tmp_next.loss_pre < loss_now:
            return False
        self.__next2trained(speed_now, loss_now)
        return True

    def __next2trained(self, speed_now: float, loss_now: float):
        node_next = heapq.heappop(self.__heap)
        node_next.speed_now = speed_now
        node_next.loss_now = loss_now
        self.__dict_trained[node_next.al] = node_next

        for al_valid in self.__iter_valid(node_next.al):
            speed_tmp, loss_tmp = self.__get_pre(al_valid)
            heapq.heappush(self.__heap, TrainUnit(al_valid, speed_tmp, loss_tmp))
            pass
        pass

    def __get_pre(self, al: ArgsLatitude):
        speed_tmp = float('inf')
        loss_tmp = float('inf')
        for al_pre in al.pre(self.__length_min, self.__layer_min, self.__hidden_min):
            node_trained = self.__dict_trained.get(al_pre)
            if node_trained.loss_now < loss_tmp:
                loss_tmp = node_trained.loss_now
                speed_tmp = node_trained.speed_now
                pass
            pass
        return speed_tmp, loss_tmp

    def __iter_valid(self, al_next: ArgsLatitude):
        for al_new in al_next.next(self.__length_max, self.__layer_max, self.__hidden_max):
            if self.__is_valid(al_new):
                yield al_new
                pass
            pass
        pass

    def __is_valid(self, al_new: ArgsLatitude):
        for al in al_new.pre(self.__length_min, self.__layer_min, self.__hidden_min):
            node_trained = self.__dict_trained.get(al)
            if node_trained is None:
                return False
            pass
        return True

    def get_next(self) -> TrainUnit:
        # 速度 > 长度 > 层数
        if len(self.__heap) == 0:
            return None
        return self.__heap[0]

    def pop(self) -> TrainUnit:
        return heapq.heappop(self.__heap)
    pass
