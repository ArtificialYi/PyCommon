import asyncio
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout, QueueException
from ...src.tool.loop_tool import LoopExecBg, NormLoop, OrderApi


class FuncTmp:
    def __init__(self) -> None:
        self.num = 0
        pass

    async def func(self):
        self.num += 1
        return await asyncio.sleep(0.1)

    async def func_err(self):
        raise Exception('func_err')
    pass


class TestLoopExecBg:
    @PytestAsyncTimeout(1)
    async def test_norm(self):
        func_tmp = FuncTmp()
        # 异常捕获器
        q_err = QueueException()
        bg = LoopExecBg(func_tmp.func)
        assert not bg.is_running
        bg.run(q_err)
        assert bg.is_running
        # 无法同时启动两个loop
        assert FuncTool.is_func_err(bg.run)

        # loop同时被两个调用方关闭
        assert await FuncTool.is_await_err(asyncio.gather(bg.stop(), bg.stop()))
        assert not bg.is_running
        # 双检锁
        assert await FuncTool.is_await_err(bg.stop())

        # Cancel异常属于常规异常，不会中断q_err的循环，会触发超时异常
        assert await FuncTool.is_await_err(
            asyncio.wait_for(q_err.exception_loop(), 0.1),
            asyncio.TimeoutError,
        )

        # bg也可以不设置异常捕获器，这样子就不会抛出任何异常
        assert not bg.is_running
        bg.run()
        assert bg.is_running
        await bg.stop()
        assert not bg.is_running
        pass

    @PytestAsyncTimeout(2)
    async def test_err(self):
        func_tmp = FuncTmp()
        # 异常捕获器
        q_err = QueueException()
        bg = LoopExecBg(func_tmp.func_err)
        assert not bg.is_running
        bg.run(q_err)
        assert bg.is_running
        # 因为异常自动结束了
        await asyncio.sleep(1)
        assert not bg.is_running

        # 因为异常结束的，所以调用stop也不会报错
        await bg.stop()
        # 异常错误会被捕获
        assert await FuncTool.is_await_err(q_err.exception_loop())
        pass
    pass


class TestNormLoop:
    @PytestAsyncTimeout(2)
    async def test(self):
        func_tmp = FuncTmp()
        norm = NormLoop(func_tmp.func)
        async with norm:
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
