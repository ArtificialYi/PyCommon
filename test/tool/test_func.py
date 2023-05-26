from concurrent.futures import ThreadPoolExecutor
import math
from time import sleep
import pytest

from ..timeout import PytestAsyncTimeout
from ...mock.func import MockException, MockFunc
from ...src.tool.func_tool import FieldSwap, lock_thread


def func_custom():
    pass


class TestFuncTool:
    @PytestAsyncTimeout(1)
    async def test(self):
        assert MockFunc.norm_sync() is None
        with pytest.raises(MockException):
            MockFunc.norm_sync_err()

        await MockFunc.norm_async()
        with pytest.raises(MockException):
            await MockFunc.norm_async_err()
            pass

        [_ async for _ in MockFunc.norm_async_gen()]
        with pytest.raises(MockException):
            [_ async for _ in MockFunc.norm_async_gen_err()]
        pass
    pass


class TestLockThread:
    NUM: int = 0

    @classmethod
    def func_unlock(cls, num):
        for _ in range(num):
            tmp = cls.NUM + 1
            sleep(0.001)
            cls.NUM = tmp
            pass
        return cls

    @classmethod
    @lock_thread
    def func_lock(cls, num):
        return cls.func_unlock(num)

    def test(self):
        # 常规调用
        assert self.__class__.NUM == 0
        assert self.__class__.func_unlock(1).NUM == 1

        # 多线程无序-如果失败，调大这个值
        num = 10
        pool_size = int(math.log(num))
        pool = ThreadPoolExecutor(pool_size)
        for _ in range(pool_size):
            pool.submit(self.__class__.func_unlock, num)
            pass
        pool.shutdown()
        assert self.__class__.NUM < num * pool_size + 1

        # 多线程有序
        num_tmp = self.__class__.NUM
        pool = ThreadPoolExecutor(pool_size)
        for _ in range(pool_size):
            pool.submit(self.__class__.func_lock, num)
            pass
        pool.shutdown()
        assert self.__class__.NUM == num * pool_size + num_tmp
        pass
    pass


class Tmp:
    TEST = None
    pass


class TestFieldSwap:
    def test_sync(self):
        """测试变换的with是否生效
        """
        field = 'TEST'
        assert getattr(Tmp, field) is None
        with FieldSwap(Tmp, field, 0):
            assert getattr(Tmp, field) == 0
            pass
        assert getattr(Tmp, field) != 0
        assert getattr(Tmp, field) is None
        pass

    @PytestAsyncTimeout(1)
    async def test_async(self):
        """测试变换的awith是否生效
        """
        field = 'TEST'
        assert getattr(Tmp, field) is None
        async with FieldSwap(Tmp, field, 0):
            assert getattr(Tmp, field) == 0
            pass
        assert getattr(Tmp, field) != 0
        assert getattr(Tmp, field) is None
        pass
    pass
