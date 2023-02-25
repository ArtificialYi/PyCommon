import asyncio


from ...src.tool.func_tool import PytestAsyncTimeout
from ...src.machine.mode import DeadWaitFlow, NormFlow


class FuncTmp:
    def __init__(self) -> None:
        self.num = 0
        pass

    async def func(self):
        self.num += 1
        return await asyncio.sleep(0.1)
    pass


class TestActionGraphSign:
    @PytestAsyncTimeout(1)
    async def test_(self):
        pass
    pass


class TestNormFlow:
    @PytestAsyncTimeout(2)
    async def test(self):
        """校验普通流
        """
        func_tmp = FuncTmp()
        norm_sign_flow = NormFlow(func_tmp.func)

        # 启动，无信号，_starting被调用
        assert func_tmp.num == 0
        assert not hasattr(norm_sign_flow, 'func')
        async with norm_sign_flow:
            assert not hasattr(norm_sign_flow, 'func')
            await asyncio.sleep(1)
            assert func_tmp.num > 0
            pass
        pass
    pass


class TestDeadWaitFlow:
    @PytestAsyncTimeout(2)
    async def test(self):
        """校验死等
        1. 构造死等流
        2. 启动流 => graph为started状态 & qsize为0 & 程序等待调用信号
        3. 多次异步调用函数后 => qsize > 0
        4. 等待部分时间后 => qsize为0
        5. exit
        """
        func_tmp = FuncTmp()
        flow = DeadWaitFlow(func_tmp.func)
        assert flow.qsize == 0
        async with flow:
            await asyncio.sleep(1)
            assert flow.qsize == 0

            assert hasattr(flow, 'func')
            for _ in range(5):
                await getattr(flow, 'func')()
                pass
            assert flow.qsize > 0
            await flow.qjoin()
            assert flow.qsize == 0
            pass
        assert flow.qsize == 0
        pass
    pass
