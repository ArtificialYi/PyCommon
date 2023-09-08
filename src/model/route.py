import heapq
import math
from typing import Dict, List, Optional
from attr import dataclass


@dataclass
class ArgsLatitude:
    length: int
    layer: int
    hidden: int

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, ArgsLatitude):  # pragma: no cover
            raise TypeError("LayerHiddenLength 只可以与 LayerHiddenLength进行比较")
        return (self.length, self.layer, self.hidden) == (__value.length, __value.layer, __value.hidden)

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, ArgsLatitude):  # pragma: no cover
            raise TypeError("LayerHiddenLength 只可以与 LayerHiddenLength进行比较")
        return (self.length, self.layer, self.hidden) < (__value.length, __value.layer, __value.hidden)

    def __le__(self, __value: object) -> bool:
        return self == __value or self < __value

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

    def next(self, al_max: 'ArgsLatitude'):
        return [
            al for al in [
                self.__next_length(al_max.length),
                self.__next_layer(al_max.layer),
                self.__next_hidden(al_max.hidden),
            ] if al is not None
        ]

    def pre(self, al_min: 'ArgsLatitude'):
        return [
            al for al in [
                self.__pre_length(al_min.length),
                self.__pre_layer(al_min.layer),
                self.__pre_hidden(al_min.hidden),
            ] if al is not None
        ]
    pass


class AlLossUnit:
    def __init__(self, al: ArgsLatitude, loss_pre: float) -> None:
        self.al = al

        self.loss_pre = loss_pre
        self.loss_now = None
        pass

    def __eq__(self, __value: object) -> bool:
        if not isinstance(__value, AlLossUnit):  # pragma: no cover
            raise TypeError("TrainUnit 只可以与 TrainUnit进行比较")
        return math.isclose(self.loss_pre, __value.loss_pre, rel_tol=1e-4, abs_tol=1e-4) and self.al == __value.al

    def __lt__(self, __value: object) -> bool:
        if not isinstance(__value, AlLossUnit):  # pragma: no cover
            raise TypeError("TrainUnit 只可以与 TrainUnit进行比较")
        if math.isclose(self.loss_pre, __value.loss_pre, rel_tol=1e-4, abs_tol=1e-4):
            return self.al > __value.al
        return self.loss_pre > __value.loss_pre
    pass


class RouteDict:
    def __init__(self, length_max: int = 1, layer_max: int = 1, length_min: int = 1, layer_min: int = 1) -> None:
        self.__dict_trained: Dict[ArgsLatitude, float] = dict()

        self.__al_min: ArgsLatitude = ArgsLatitude(length_min, layer_min, 2 ** layer_min)
        self.__al_max: ArgsLatitude = ArgsLatitude(length_max, layer_max, 2 ** layer_max)
        pass

    def pre_is_all_trained(self, al: ArgsLatitude) -> bool:
        for al_pre in al.pre(self.__al_min):
            if self.__dict_trained.get(al_pre) is None:
                return False
            pass
        return True

    def can_push(self, al: ArgsLatitude) -> bool:
        # 节点在范围内 and 当前未训练 and 所有前置已训练
        return self.__al_min <= al <= self.__al_max and self.__dict_trained.get(al) is None and self.pre_is_all_trained(al)

    def iter_next(self, al: ArgsLatitude):
        for al_next in al.next(self.__al_max):
            if self.pre_is_all_trained(al_next):
                yield al_next
            pass
        pass

    def loss_pre(self, al: ArgsLatitude) -> float:
        loss_pre = float('inf')
        for al_pre in al.pre(self.__al_min):
            loss = self.__dict_trained.get(al_pre)
            if loss < loss_pre:
                loss_pre = loss
                pass
            pass
        return loss_pre

    def set(self, al: ArgsLatitude, loss: float):
        self.__dict_trained[al] = loss
        pass

    def get(self, al: ArgsLatitude) -> Optional[float]:
        return self.__dict_trained.get(al)
    pass


class RouteHeap:
    def __init__(self, route_dict: RouteDict) -> None:
        # 待训练堆
        self.__heap: List[AlLossUnit] = [AlLossUnit(ArgsLatitude(1, 1, 2), float('inf'))]
        # 已训练字典
        self.__route_dict = route_dict
        pass

    def push(self, al: ArgsLatitude, loss: float, loss_valid: bool = False) -> bool:
        al_bool = loss_valid and loss >= self.__route_dict.loss_pre(al)
        # 过滤al
        if al_bool or not self.__route_dict.can_push(al):
            return False

        # 已训练字典更新
        self.__route_dict.set(al, loss)
        # 生成全新节点
        for al_next in self.__route_dict.iter_next(al):
            heapq.heappush(self.__heap, AlLossUnit(al_next, self.__route_dict.loss_pre(al_next)))
            pass
        return True

    def pop(self) -> Optional[AlLossUnit]:
        if len(self.__heap) == 0:
            return None
        return heapq.heappop(self.__heap)

    def get(self, al: ArgsLatitude) -> Optional[float]:
        return self.__route_dict.get(al)
    pass


class RouteUnit:
    def __init__(self, heap_now: RouteHeap, heap_pre: RouteHeap) -> None:
        self.__heap_now = heap_now
        self.__heap_pre = heap_pre
        pass

    def push(self, al: ArgsLatitude, loss: Optional[float]) -> bool:
        if loss is None:
            return False
        return self.__heap_now.push(al, loss, True)

    def pop(self):
        node_now = self.__heap_now.pop()
        while node_now is not None and self.push(node_now.al, self.__heap_pre.get(node_now.al)):
            node_now = self.__heap_now.pop()
            pass
        return node_now
    pass
