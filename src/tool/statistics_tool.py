

class StatisticsTool:
    @staticmethod
    def cal_var(n_pre: int, var_pre: float, avg_pre: float, avg_now: float, x: float):
        if n_pre <= 0:
            return 0

        # 这个也可以，放弃的原因是扩展性没有另一个好
        # return ((n_pre - 1) * var_pre + (x - avg_pre) ** 2 - (n_pre + 1) * (avg_now - avg_pre) ** 2) / n_pre
        return ((n_pre - 1) * var_pre + n_pre * (avg_now - avg_pre) ** 2 + (x - avg_now) ** 2) / n_pre
    pass


class StatisticsContainer:
    def __init__(self) -> None:
        self.__n_now = 0
        self.__sum_now = 0
        self.__avg_now = 0
        self.__var_now = 0
        self.__std_now = 0
        pass

    def add(self, x: float):
        self.__n_pre = self.__n_now
        self.__sum_pre = self.__sum_now
        self.__avg_pre = self.__avg_now
        self.__var_pre = self.__var_now

        self.__n_now = self.__n_pre + 1
        self.__sum_now = self.__sum_pre + x
        self.__avg_now = self.__sum_now / self.__n_now
        self.__var_now = StatisticsTool.cal_var(self.__n_pre, self.__var_pre, self.__avg_pre, self.__avg_now, x)
        self.__std_now = self.__var_now ** 0.5
        return self

    @property
    def count(self):
        return self.__n_now

    @property
    def sum(self):
        return self.__sum_now

    @property
    def avg(self):
        return self.__avg_now

    @property
    def var(self):
        return self.__var_now

    @property
    def std(self):
        return self.__std_now
    pass
