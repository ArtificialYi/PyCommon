from typing import Callable


class Map:
    def __init__(self, func: Callable) -> None:
        self.__map = dict()
        self.__func = func
        pass

    def get_func_value(self, key, *args, **kwds):
        if self.__map.get(key, None) is not None:
            return self.__map[key]

        self.__map[key] = self.__func(*args, **kwds)
        return self.__map[key]

    def get_norm_value(self, key, default):
        return self.__map.get(key, default)
    pass


class MapKeyOne(Map):
    def get_func_value(self, key, *args, **kwds):
        return super().get_func_value(key, key, *args, **kwds)
    pass
