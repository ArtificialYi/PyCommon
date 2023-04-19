import asyncio
from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout, QueueException
from ...src.tool.loop_tool import LoopExecBg


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
    async def test_loop_exec_bg(self):
        func_tmp0 = FuncTmp()
        # 异常捕获器
        q_err = QueueException()
        bg = LoopExecBg(func_tmp0.func)
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

        # Cancel异常属于常规异常
        assert await FuncTool.is_await_err(asyncio.wait_for(q_err.exception_loop(), 0.1))
        pass
    pass
