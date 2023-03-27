import asyncio
from time import sleep


class MockDelay:
    def __init__(self, delay: float = 0.01) -> None:
        self.__delay = delay
        pass

    def mock_sleep(self, delay=None):
        sleep(self.__delay if delay is None else delay)
        pass

    async def mock_asleep(self, delay=None):
        await asyncio.sleep(self.__delay if delay is None else delay)
        pass

    def mock_set_delay(self, delay: float):
        self.__delay = delay
        pass
    pass
