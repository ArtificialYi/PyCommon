from ..src.tool.map_tool import MapKey


@MapKey()
async def get_mock_logger():
    return MockLogger()


class MockLogger:
    @staticmethod
    async def debug(*args, **kwds):
        print(*args, **kwds)
        pass

    @staticmethod
    async def info(*args, **kwds):
        print(*args, **kwds)
        pass

    @staticmethod
    async def warning(*args, **kwds):
        print(*args, **kwds)
        pass

    @staticmethod
    async def error(*args, **kwds):
        print(*args, **kwds)
        pass

    @staticmethod
    async def exception(*args, **kwds):
        print(*args, **kwds)
        pass
    pass
