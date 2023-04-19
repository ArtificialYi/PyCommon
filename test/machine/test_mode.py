# import asyncio


# from ...src.tool.func_tool import FuncTool, PytestAsyncTimeout, QueueException


# class FuncTmp:
#     def __init__(self) -> None:
#         self.num = 0
#         pass

#     async def func(self):
#         self.num += 1
#         return await asyncio.sleep(0.1)

#     async def func_err(self):
#         raise Exception('func_err')
#     pass


# class TestActionGraphSign:
#     @PytestAsyncTimeout(3)
#     async def test_err_sync(self):
#         """同步运行两个会报错
#         """
#         func_tmp = FuncTmp()
#         machine = SGMachineForFlow(SGForFlow(func_tmp.func))
#         action_sign = ActionGraphSign(machine)
#         # 启动流
#         async with machine:
#             assert func_tmp.num == 0
#             assert action_sign.run() is None
#             await asyncio.sleep(1)
#             assert func_tmp.num > 0
#             assert FuncTool.is_func_err(action_sign.run)
#         # TODO: 如果超时了，就调大超时时间
#         while action_sign.is_running:
#             await asyncio.sleep(0.1)
#             pass
#         pass
#     pass


# class TestNormFlow:
#     @PytestAsyncTimeout(2)
#     async def test_norm(self):
#         """校验普通流
#         """
#         # 普通运行时：启动，无信号，_starting被调用
#         func_tmp = FuncTmp()
#         norm_sign_flow = NormFlow(func_tmp.func)

#         assert func_tmp.num == 0
#         assert not hasattr(norm_sign_flow, 'func')
#         async with norm_sign_flow:
#             assert not hasattr(norm_sign_flow, 'func')
#             await asyncio.sleep(1)
#             assert func_tmp.num > 0
#             pass
#         pass

#     @PytestAsyncTimeout(2)
#     async def test_none(self):
#         """校验无starting普通流
#         """
#         # starting为None的运行时：启动，无信号，_starting卡死等待退出信号
#         none_sign_flow = NormFlow(None)  # type: ignore
#         async with none_sign_flow:
#             await asyncio.sleep(1)
#             pass
#         pass

#     @PytestAsyncTimeout(1)
#     async def test_err_sync(self):
#         """同步运行会报错
#         1. 不能在流启动时启动
#         2. 不能在流未启动时关闭
#         """
#         func_tmp = FuncTmp()
#         norm_sign_flow = NormFlow(func_tmp.func)
#         assert await FuncTool.is_async_err(norm_sign_flow.__aexit__, None, None, None)
#         async with norm_sign_flow:
#             assert await FuncTool.is_async_err(norm_sign_flow.__aenter__)
#             pass
#         assert await FuncTool.is_async_err(norm_sign_flow.__aexit__, None, None, None)
#         pass

#     @PytestAsyncTimeout(1)
#     async def test_err_safe(self):
#         """并发运行会报错
#         1. 流启动不能并发
#         """
#         func_tmp = FuncTmp()
#         norm_sign_flow = NormFlow(func_tmp.func)
#         assert await FuncTool.is_async_err(asyncio.gather, norm_sign_flow.__aenter__, norm_sign_flow.__aenter__)
#         pass

#     @PytestAsyncTimeout(1)
#     async def test_err_func(self):
#         """异常捕获
#         """
#         func_tmp = FuncTmp()
#         q_exception = QueueException()
#         # 常规流
#         flow_norm = NormFlow(func_tmp.func, q_exception)
#         async with flow_norm:
#             pass

#         # 异常流
#         flow_err = NormFlow(func_tmp.func_err, q_exception)
#         async with flow_err:
#             assert await FuncTool.is_async_err(q_exception.exception_loop)
#             pass
#         pass
#     pass


# class TestDeadWaitFlow:
#     @PytestAsyncTimeout(2)
#     async def test(self):
#         """校验死等
#         1. 构造死等流
#         2. 启动流 => graph为started状态 & qsize为0 & 程序等待调用信号
#         3. 多次异步调用函数后 => qsize > 0
#         4. 等待部分时间后 => qsize为0
#         5. exit
#         """
#         func_tmp = FuncTmp()
#         flow = DeadWaitFlow(func_tmp.func)
#         assert flow.qsize == 0
#         async with flow:
#             await asyncio.sleep(1)
#             assert flow.qsize == 0

#             assert hasattr(flow, 'func')
#             for _ in range(5):
#                 await getattr(flow, 'func')()
#                 pass
#             assert flow.qsize > 0
#             await flow.qjoin()
#             assert flow.qsize == 0
#             pass
#         assert flow.qsize == 0
#         pass

#     @PytestAsyncTimeout(2)
#     async def test_err_sync(self):
#         func_tmp = FuncTmp()
#         assert await FuncTool.is_async_err(func_tmp.func_err)
#         flow = DeadWaitFlow(func_tmp.func_err)
#         async with flow:
#             assert flow.exception is None
#             await getattr(flow, 'func_err')()
#             await asyncio.sleep(1)
#             assert flow.exception is not None
#             pass
#         assert flow.exception is not None
#         pass
#     pass
