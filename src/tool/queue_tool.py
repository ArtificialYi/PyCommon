from collections import deque
from typing import Deque
from attr import dataclass


@dataclass
class AvgData:
    num: float
    sum: float
    pass


class MovingAvg:
    def __init__(self, length: int, default: float) -> None:
        self.__queue: Deque[AvgData] = deque([AvgData(0, 0)], maxlen=length + 1)
        for _ in range(length):
            self.push(default)
            pass
        self.__len = length
        pass

    def avg(self):
        return (self.__queue[-1].sum - self.__queue[0].sum) / self.__len

    def push(self, num: float):
        self.__queue.append(AvgData(num, self.__queue[-1].sum + num))
        pass

    def avg_target(self, target: float):
        sum_target = target * self.__len
        sum_current = self.__queue[-1].sum - self.__queue[1].sum
        return sum_target - sum_current
    pass
