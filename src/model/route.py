import heapq
import math
from typing import Dict


class ArgsLatitude:
    def __init__(self, length: int, layer: int, hidden: int):
        self.length = length
        self.layer = layer
        self.hidden = hidden
        pass

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ArgsLatitude):
            raise TypeError("LayerHiddenLength 只可以与 LayerHiddenLength进行比较")
        return (self.length, self.layer) == (__value.length, __value.layer)

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, ArgsLatitude):
            raise TypeError("LayerHiddenLength 只可以与 LayerHiddenLength进行比较")
        return (self.length, self.layer) < (__value.length, __value.layer)

    def __hash__(self) -> int:
        return hash(self.hidden)

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
        if hidden_pre < hidden_min:
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
    def __init__(self, al: ArgsLatitude, speed_pre: float, loss_pre: float) -> None:
        self.al = al
        self.speed_pre = speed_pre
        self.loss_pre = loss_pre

        self.speed_now = None
        self.loss_now = None
        pass

    @property
    def is_ok(self):
        return self.loss_now is not None

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, TrainUnit):
            raise TypeError("TrainUnit 只可以与 TrainUnit进行比较")
        return math.isclose(self.speed_pre, __value.speed_pre, rel_tol=1e-4, abs_tol=1e-4) and self.al == __value.al

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, TrainUnit):
            raise TypeError("TrainUnit 只可以与 TrainUnit进行比较")
        if math.isclose(self.speed_pre, __value.speed_pre, rel_tol=1e-4, abs_tol=1e-4):
            return self.al < __value.al
        return self.speed_pre > __value.speed_pre

    def set_loss(self, speed: float, loss: float):
        if math.isclose(loss, self.loss_pre, rel_tol=1e-4, abs_tol=1e-4) or loss > self.loss_pre:
            return False
        self.speed_now = speed
        self.loss_now = loss
        return True
    pass


class Route:
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

    def add_node(self, speed_now: float, loss_now: float):
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
    pass
