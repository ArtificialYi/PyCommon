import asyncio
import pytest

from ...src.tool.base import AsyncBase
from ...mock.func import MockException
from ...src.exception.tool import AlreadyRunException
from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.tool.loop_tool import LoopExecBg, NormLoop, OrderApi


class FuncTmp:
    def __init__(self) -> None:
        self.num = 0
        pass

    async def func(self):
        self.num += 1
        return await asyncio.sleep(0.1)

    async def func_err(self):
        raise MockException('func_err')
    pass


class TestLoopExecBg:
    @PytestAsyncTimeout(1)
    async def test_norm(self):
        func_tmp = FuncTmp()
        bg = LoopExecBg(func_tmp.func)
        with pytest.raises(asyncio.CancelledError):
            await bg.task
        bg.run()
        with pytest.raises(asyncio.TimeoutError):
            await AsyncBase.wait_err(bg.task, 0.1)
        # 无法同时启动两个loop
        with pytest.raises(AlreadyRunException):
            bg.run()

        # 关闭可以调用多次
        await bg.stop()
        await bg.stop()
        await asyncio.gather(bg.stop(), bg.stop())
        pass

    @PytestAsyncTimeout(1)
    async def test_err(self):
        func_tmp = FuncTmp()
        bg = LoopExecBg(func_tmp.func_err)
        with pytest.raises(asyncio.CancelledError):
            await bg.task

        bg.run()
        with pytest.raises(MockException):
            await bg.task
        await bg.stop()
        with pytest.raises(MockException):
            await bg.task
        pass
    pass


class TestNormLoop:
    @PytestAsyncTimeout(2)
    async def test(self):
        func_tmp = FuncTmp()
        async with NormLoop(func_tmp.func):
            assert func_tmp.num == 0
            await asyncio.sleep(1)
            assert func_tmp.num > 0
            pass
        pass
    pass


class TestOrderApi:
    class Tmp(OrderApi):
        def __init__(self) -> None:
            self.num = 0
            OrderApi.__init__(self, self.func)
            pass

        async def func(self):
            self.num += 1
            return await asyncio.sleep(0.1)
        pass

    @PytestAsyncTimeout(1)
    async def test(self):
        order = TestOrderApi.Tmp()
        assert order.num == 0
        await order.func()
        assert order.num == 1
        async with order:
            assert order.num == 1
            future: asyncio.Future = await order.func()  # type: ignore
            assert order.num == 1
            await future
            assert order.num == 2
            pass
        pass
    pass
