import asyncio

from ...src.tool.base import AsyncBase

from ...mock.func import MockException

from ...src.exception.tool import AlreadyStopException
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout
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
        assert await bg is None
        bg.run()
        assert await FuncTool.await_err(AsyncBase.wait_err(bg, 0.1), asyncio.TimeoutError)
        # 无法同时启动两个loop
        assert FuncTool.is_func_err(bg.run)

        # loop同时被两个调用方关闭
        # TODO: 添加异常类型
        assert await FuncTool.await_err(asyncio.gather(bg.stop(), bg.stop()), AlreadyStopException)
        assert await bg is None
        # 双检锁
        assert await FuncTool.await_err(bg.stop(), AlreadyStopException)
        pass

    @PytestAsyncTimeout(2)
    async def test_err(self):
        func_tmp = FuncTmp()
        bg = LoopExecBg(func_tmp.func_err)
        assert await bg is None
        bg.run()
        assert await FuncTool.await_err(bg, MockException)

        # 因为异常结束的，所以调用stop也不会报错
        await bg.stop()
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
