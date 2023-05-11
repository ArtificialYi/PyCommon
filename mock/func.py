class MockException(Exception):
    """Mock的Exception
    """
    pass


class MockFunc:
    @staticmethod
    async def norm_async(*args, **kwds):
        pass

    @staticmethod
    async def norm_async_err():
        raise MockException('会抛出异常的coro函数')

    @staticmethod
    async def norm_async_gen():
        yield
        pass

    @staticmethod
    async def norm_async_gen_err():
        yield
        raise MockException('会抛出异常的async gen')

    @staticmethod
    def norm_sync():
        pass

    @staticmethod
    def norm_sync_err():
        raise MockException('会抛出异常的func')
    pass
