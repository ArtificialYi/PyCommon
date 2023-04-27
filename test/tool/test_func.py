from concurrent.futures import ThreadPoolExecutor
import math
from time import sleep

from ...mock.func import MockException, MockFunc
from ...src.tool.func_tool import (
    CallableDecoratorAsync, FieldSwap, FuncTool,
    LockThread, PytestAsyncTimeout
)


def func_custom():
    pass


class TestFuncTool:
    @PytestAsyncTimeout(1)
    async def test(self):
        assert not FuncTool.is_func_err(MockFunc.norm_sync)
        assert FuncTool.is_func_err(MockFunc.norm_sync_err)

        assert not await FuncTool.is_await_err(MockFunc.norm_async())
        assert await FuncTool.is_await_err(MockFunc.norm_async_err(), MockException)

        assert not await FuncTool.is_async_gen_err(MockFunc.norm_async_gen())
        assert await FuncTool.is_async_gen_err(MockFunc.norm_async_gen_err(), MockException)
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
    @LockThread
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


class TestCallableDecoratorAsync:
    async def func_decorator(self, func_async, obj, *args, **kwds):
        return False

    async def func_tmp(self):
        return True

    def __init_err(self):
        flag = False
        try:
            CallableDecoratorAsync(MockFunc.norm_sync)
            assert False
        except Exception:
            flag = True
        assert flag

    @PytestAsyncTimeout(1)
    async def test(self):
        # 无法使用同步函数构造
        self.__init_err()

        decorator = CallableDecoratorAsync(self.func_decorator)
        # 无法对同步函数封装
        flag = False
        try:
            decorator(MockFunc.norm_sync)
            assert False
        except Exception:
            flag = True
        assert flag

        # 常规
        assert await self.func_tmp()
        assert not await decorator(self.func_tmp)(self)
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
