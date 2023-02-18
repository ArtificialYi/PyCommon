from typing import Callable


class Map:
    def __init__(self, func: Callable) -> None:
        self.__map = dict()
        self.__func = func
        pass

    def get_value(self, key, *args, **kwds):
        if self.__map.get(key, None) is not None:
            return self.__map[key]

        self.__map[key] = self.__func(*args, **kwds)
        return self.__map[key]
    pass


class MapKeyOne(Map):
    def get_value(self, key):
        return super().get_value(key, key)
    pass
