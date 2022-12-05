import asyncio
from ...src.tool.base import AsyncBase, BaseTool
from ...src.tool.func_tool import AsyncExecOrder, AsyncExecOrderHandle, FuncTool
import pytest


class TestAsyncExecOrder:
    @pytest.mark.timeout(4)
    @pytest.mark.asyncio
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
        handle = AsyncExecOrderHandle()
        assert not hasattr(handle, 'return_self')
        handle.func_sync(BaseTool.return_self)
        assert hasattr(handle, 'return_self')
        delattr(handle, 'return_self')
        assert not hasattr(handle, 'return_self')
        handle.func_async(BaseTool.return_self)
        assert hasattr(handle, 'return_self')

        # 对象函数有序化
        assert not hasattr(handle, 'test')
        handle.func_sync(self.test)
        assert hasattr(handle, 'test')
        delattr(handle, 'test')
        assert not hasattr(handle, 'test')
        handle.func_async(self.test)
        assert hasattr(handle, 'test')

        # 模块函数有序化
        assert not hasattr(handle, 'func_custom')
        handle.func_sync(func_custom)
        assert hasattr(handle, 'func_custom')
        delattr(handle, 'func_custom')
        assert not hasattr(handle, 'func_custom')
        handle.func_async(func_custom)
        assert hasattr(handle, 'func_custom')
        pass
    pass


class TestFuncTool:
    @pytest.mark.timeout(1)
    @pytest.mark.asyncio
    async def test(self):
        assert not await FuncTool.is_func_err(FuncTool.norm_sync)
        assert not await FuncTool.is_func_err(FuncTool.norm_async)
        assert await FuncTool.is_func_err(FuncTool.norm_sync_err)
        assert await FuncTool.is_func_err(FuncTool.norm_async_err)
        pass
    pass
