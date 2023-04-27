from contextlib import asynccontextmanager

from .func_tool import FuncTool

from .base import AsyncBase


class AsyncTool:
    @staticmethod
    @asynccontextmanager
    async def coro_async_gen(coro):
        task = AsyncBase.coro2task_exec(coro)
        yield task
        task.cancel()
        await FuncTool.await_no_cancel(task)
        pass
    pass
