
from .db.base import MockDelay


async def get_mock_logger():
    return MockLog()


class MockLog(MockDelay):
    async def debug(self, *args, **kwds) -> None:
        await self.mock_asleep()

    async def info(self, *args, **kwds) -> None:
        await self.mock_asleep()

    async def warning(self, *args, **kwds) -> None:
        await self.mock_asleep()

    async def error(self, *args, **kwds) -> None:
        await self.mock_asleep()

    async def shutdown(self) -> None:
        await self.mock_asleep()
    pass
