import asyncio
from ...src.tool.base import AsyncBase, BaseTool
from ...src.tool.func_tool import CallableOrder, FuncTool
import pytest


class TestCallableOrder:
    @pytest.mark.timeout(2)
    @pytest.mark.asyncio
    async def test(self):
        # 无信号-不等待调用，啥也没发生
        call_order = CallableOrder(BaseTool.return_self)
        assert not await call_order.queue_no_wait()
        # 无信号-等待调用，锁死
        task = AsyncBase.coro2task_exec(call_order.queue_wait())
        await asyncio.sleep(1)
        assert not task.done()
        # 产生信号，之前的等待直接生效
        assert await call_order.call(5) == 5
        assert task.done()
        assert await task
        pass
    pass


class TestFuncTool:
    def __func_norm(self):
        pass

    async def __coro_norm(self):
        pass

    def __func_err(self):
        raise Exception('异常函数')

    async def __coro_err(self):
        raise Exception('异常coro')

    @pytest.mark.timeout(1)
    @pytest.mark.asyncio
    async def test(self):
        assert not await FuncTool.func_err(self.__func_norm)
        assert not await FuncTool.func_err(self.__coro_norm)
        assert await FuncTool.func_err(self.__func_err)
        assert await FuncTool.func_err(self.__coro_err)
        pass
    pass
