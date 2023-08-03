import heapq
import math
from typing import List


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

    def next_length(self, length_max: int):
        length_next = self.length * 2
        if length_next > length_max:
            return None
        return ArgsLatitude(length_next, self.layer, self.hidden)

    def pre_length(self, length_min: int):
        length_pre = self.length // 2
        if length_pre < length_min:
            return None
        return ArgsLatitude(length_pre, self.layer, self.hidden)

    def next_layer(self, layer_max: int):
        layer_next = self.layer + 1
        if layer_next > layer_max or 2 ** layer_next > self.hidden:
            return None
        return ArgsLatitude(self.length, layer_next, self.hidden)

    def pre_layer(self, layer_min: int):
        layer_pre = self.layer - 1
        if layer_pre < layer_min:
            return None
        return ArgsLatitude(self.length, layer_pre, self.hidden)

    def next_hidden(self, hidden_max: int):
        hidden_next = self.hidden * 2
        if hidden_next > hidden_max:
            return None
        return ArgsLatitude(self.length, self.layer, hidden_next)

    def pre_hidden(self, hidden_min: int):
        hidden_pre = self.hidden // 2
        if hidden_pre < hidden_min:
            return None
        return ArgsLatitude(self.length, self.layer, hidden_pre)
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

    def next(self, length_max: int, layer_max: int, hidden_max: int):
        if not self.is_ok:
            return []

        return [
            TrainUnit(al, self.speed_now, self.loss_now)
            for al in [
                self.al.next_length(length_max),
                self.al.next_layer(layer_max),
                self.al.next_hidden(hidden_max),
            ] if al is not None
        ]

    def pre(self, length_min: int, layer_min: int, hidden_min: int) -> List[ArgsLatitude]:
        if not self.is_ok:
            return []

        return [
            al for al in [
                self.al.pre_length(length_min),
                self.al.pre_layer(layer_min),
                self.al.pre_hidden(hidden_min),
            ] if al is not None
        ]
    pass


class Route:
    def __init__(self, length_max: int = 1, layer_max: int = 1):
        key_tmp = ArgsLatitude(1, 1, 2)
        value_tmp = TrainUnit(key_tmp, float('inf'), float('inf'))

        # 待训练堆(以速度排序)
        self.__heap = [value_tmp]
        # 待训练字典
        self.__dict_wait = {
            key_tmp: value_tmp
        }
        # 已训练集合
        self.__set_trained = set()

        self.__length_max = length_max
        self.__layer_max = layer_max
        self.__hidden_max = 2 ** self.__layer_max
        pass

    def add_note(self, train_res: TrainUnit):
        # 生成新节点
        for train_unit in train_res.next(self.__length_max, self.__layer_max, self.__hidden_max):
            heap_unit = self.__add(train_unit)

            # 旧节点更优
            if heap_unit is None or heap_unit.loss_pre < train_res.loss_now:
                continue

            # 替换
            self.__replace(train_unit)
            pass
        pass

    def __add(self, train_unit: TrainUnit):
        heap_unit = self.__dict_wait.get(train_unit.al)
        if heap_unit is None:
            self.__dict_wait[train_unit.al] = train_unit
            heapq.heappush(self.__heap, train_unit)
            pass
        return heap_unit

    def __replace(self, train_unit: TrainUnit):
        for heap_unit in self.__heap:
            if heap_unit.al == train_unit.al:
                heap_unit.loss_pre = train_unit.loss_pre
                heap_unit.speed_pre = train_unit.speed_pre
                break
        else:
            raise Exception(f'heap中不存在该节点: {train_unit.al.__dict__}')
        heapq.heapify(self.__heap)
        pass

    def get_next(self) -> TrainUnit:
        # 速度 > 长度 > 层数
        if len(self.__heap) == 0:
            return None
        return self.__heap[0]
    pass
