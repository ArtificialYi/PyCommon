import sys
from typing import Generator, Optional
from attr import dataclass, ib

from ..tool.map_tool import MapKeySelf


@dataclass(hash=True)
class ArgsLatitude:
    """普通的数据类
    1. hidden_max=2**layer_max
    2. hidden >= 2**layer >= 2
    3. layer_min = 1
    """
    hidden: int = ib(converter=int, kw_only=True)
    layer: int = ib(converter=int, kw_only=True)
    loss: float = ib(default=float('inf'), converter=float, kw_only=True, eq=False)

    def __attrs_post_init__(self):
        if not self.__valid(self.hidden, self.layer):
            raise ValueError(f'DataNorm不支持该参数组合:hidden-{self.hidden},layer-{self.layer}')

    @staticmethod
    def __valid(hidden: int, layer: int, hidden_min: int = 2, hidden_max: int = sys.maxsize):
        hidden_bool = hidden_min <= hidden <= hidden_max
        return hidden_bool and 2 <= 2 ** layer <= hidden

    def iter_next(self, hidden_max: int) -> Generator[tuple[int, int], None, None]:
        layer_next = self.layer + 1
        if self.__valid(self.hidden, layer_next, hidden_max=hidden_max):
            yield self.hidden, layer_next
            pass

        hidden_next = self.hidden * 2
        if self.__valid(hidden_next, self.layer, hidden_max=hidden_max):
            yield hidden_next, self.layer
            pass
        pass

    def iter_pre(self, hidden_min: int) -> Generator[tuple[int, int], None, None]:
        layer_next = self.layer - 1
        if self.__valid(self.hidden, layer_next, hidden_min=hidden_min):
            yield self.hidden, layer_next
            pass

        hidden_next = self.hidden // 2
        if self.__valid(hidden_next, self.layer, hidden_min=hidden_min):
            yield hidden_next, self.layer
            pass
        pass

    def set_loss(self, loss: float):
        if loss < self.loss:
            self.loss = loss
            pass
        pass

    @staticmethod
    def key_sorted(obj: 'ArgsLatitude') -> tuple[float, int, int]:
        return (-obj.loss, obj.hidden, obj.layer)
    pass


class ArgsLatitudeManage:
    def __init__(self, hidden_max: int):
        self.__hidden_max = hidden_max
        pass

    @MapKeySelf(ArgsLatitude)
    def __data_create(self, *, hidden: int, layer: int) -> ArgsLatitude:
        return ArgsLatitude(hidden=hidden, layer=layer)

    def create(self, hidden: int, layer: int, loss: float = float('inf')) -> ArgsLatitude:
        data = self.__data_create(hidden=hidden, layer=layer)
        data.set_loss(loss)
        return data

    def get_next(self, data: ArgsLatitude, loss: float) -> Optional[set[ArgsLatitude]]:
        if loss >= data.loss:
            return None

        return {
            self.create(hidden=hidden, layer=layer, loss=loss)
            for hidden, layer in data.iter_next(self.__hidden_max)
        }
    pass


class RouteManage:
    """Route管理类
    """
    def __init__(self, hidden_min: int, hidden_max: int) -> None:
        self.__data_manage = ArgsLatitudeManage(hidden_max)
        self.__hidden_min = hidden_min

        self.__set_next: set[ArgsLatitude] = set()
        self.__set_pop: set[ArgsLatitude] = set()
        self.__set_pop_id: set[int] = set()
        self.__set_old: set[ArgsLatitude] = set()
        self.__set_all: set[ArgsLatitude] = set()

        self.__next_add(self.__data_manage.create(hidden=self.__hidden_min, layer=1))
        pass

    def __check(self):  # pragma: no cover
        if self.__set_old & self.__set_pop & self.__set_next:
            raise Exception(f'业务错误: old集合{self.__set_old} 与 pop集合{self.__set_pop} 与 next集合{self.__set_next} 有交集')
        pass

    def __next2pop(self, unit: ArgsLatitude):
        self.__set_next.remove(unit)
        self.__set_pop.add(unit)
        self.__set_pop_id.add(id(unit))
        pass

    def __pop2old(self, unit: ArgsLatitude):
        self.__set_pop.remove(unit)
        self.__set_pop_id.remove(id(unit))
        self.__set_old.add(unit)
        pass

    def __next_add(self, unit: ArgsLatitude):
        self.__set_next.add(unit)
        self.__set_all.add(unit)
        pass

    def pop(self) -> ArgsLatitude:
        """弹出一个元素
        1. 从next集合中弹出一个元素至pop集合
        """
        self.__check()
        if not self.__set_next:
            return None

        unit = sorted(self.__set_next, key=ArgsLatitude.key_sorted, reverse=True).pop()
        self.__next2pop(unit)
        return unit

    def reset(self) -> 'RouteManage':
        """pop2next
        """
        while self.__set_pop:
            unit = self.__set_pop.pop()
            self.__set_pop_id.remove(id(unit))
            self.__set_next.add(unit)
            pass
        return self

    def __iter_pre(self, set_next: set[ArgsLatitude]) -> Generator[ArgsLatitude, None, None]:
        for data in set_next:
            if data not in self.__set_all and all(
                self.__data_manage.create(hidden=hidden, layer=layer) in self.__set_old
                for hidden, layer in data.iter_pre(self.__hidden_min)
            ):
                yield data
                pass
            pass
        pass

    def __push_err(self, unit: ArgsLatitude) -> bool:
        if id(unit) not in self.__set_pop_id:
            raise Exception(f'业务错误: {unit}不在可push集合{list(self.__set_pop)}中')

    def push(self, unit: ArgsLatitude, loss: float) -> bool:
        self.__push_err(unit)

        set_next = self.__data_manage.get_next(unit, loss)
        if set_next is None:
            return False

        self.__pop2old(unit)
        for data in self.__iter_pre(set_next):
            self.__next_add(data)
            pass
        return True
    pass
