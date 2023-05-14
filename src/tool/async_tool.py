from contextlib import asynccontextmanager


from .base import AsyncBase


class AsyncTool:
    @staticmethod
    @asynccontextmanager
    async def coro_async_gen(coro):
        task = AsyncBase.coro2task_exec(coro)
        yield task
        await task
        pass
    pass
