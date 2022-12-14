import asyncio
from concurrent.futures import ThreadPoolExecutor
import math
from ...src.tool.base import AsyncBase, BaseTool
from ...src.tool.func_tool import AsyncExecOrder, AsyncExecOrderHandle, CallableDecoratorAsync, Func2CallableOrderAsync, Func2CallableOrderSync, FuncTool, LockThread, PytestAsync


class TestAsyncExecOrder:
    @PytestAsync(4)
    async def test(self):
        # 无信号-不等待调用，啥也没发生
        call_order = AsyncExecOrder(BaseTool.return_self)
        assert not await call_order.queue_no_wait()
        # 无信号-等待调用，锁死
        task = AsyncBase.coro2task_exec(call_order.queue_wait())
        await asyncio.sleep(1)
        assert not task.done()
        # 产生信号，之前的等待直接生效
        assert await call_order.call_sync(5) == 5
        assert task.done()
        assert await task

        # 产生空信号，但是不消费，产生堆积
        await call_order.call_step()
        await asyncio.sleep(1)
        assert call_order.qsize == 1

        # 产生新信号，但是不消费，产生堆积
        await call_order.call_async(5)
        await asyncio.sleep(1)
        assert call_order.qsize == 2

        # 将信号消费
        assert await call_order.queue_wait()
        assert call_order.qsize == 1
        assert await call_order.queue_wait()
        assert call_order.qsize == 0
        pass
    pass


def func_custom():
    pass


class TestAsyncExecOrderHandle:
    def test(self):
        # 类函数有序化
        handle_sync = Func2CallableOrderSync(BaseTool.return_self)
        assert hasattr(handle_sync, 'return_self')
        handle_async = Func2CallableOrderAsync(BaseTool.return_self)
        assert hasattr(handle_async, 'return_self')

        # 对象函数有序化
        handle_sync = Func2CallableOrderSync(self.test)
        assert hasattr(handle_sync, 'test')
        handle_async = Func2CallableOrderAsync(self.test)
        assert hasattr(handle_async, 'test')

        # 模块函数有序化
        handle_sync = Func2CallableOrderSync(func_custom)
        assert hasattr(handle_sync, 'func_custom')
        handle_async = Func2CallableOrderAsync(func_custom)
        assert hasattr(handle_async, 'func_custom')
        pass
    pass


class TestFuncTool:
    @PytestAsync(1)
    async def test(self):
        assert not await FuncTool.is_func_err(FuncTool.norm_sync)
        assert not await FuncTool.is_func_err(FuncTool.norm_async)
        assert await FuncTool.is_func_err(FuncTool.norm_sync_err)
        assert await FuncTool.is_func_err(FuncTool.norm_async_err)
        pass
    pass


class TestLockThread:
    NUM: int = 0

    @classmethod
    def func_unlock(cls, num):
        for _ in range(num):
            cls.NUM += 1
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
        num = 20000
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

    @PytestAsync(1)
    async def test(self):
        # 无法使用同步函数构造
        flag = False
        try:
            CallableDecoratorAsync(FuncTool.norm_sync)
            assert False
        except Exception:
            flag = True
        finally:
            assert flag
            pass

        decorator = CallableDecoratorAsync(self.func_decorator)
        # 无法对同步函数封装
        flag = False
        try:
            decorator(FuncTool.norm_sync)
            assert False
        except Exception:
            flag = True
        finally:
            assert flag
            pass

        # 常规
        assert await self.func_tmp()
        assert not await decorator(self.func_tmp)(self)
        pass
    pass
