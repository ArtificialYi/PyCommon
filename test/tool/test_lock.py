import asyncio

from ...src.tool.lock_tool import DCLGlobalAsync


class TestDCLGlobalAsync:
    @DCLGlobalAsync()
    async def __opt(self) -> int:
        assert type(self).__name__ == 'TestDCLGlobalAsync'
        await asyncio.sleep(0.01)
        return 42

    async def test(self):
        # 双检操作
        res0, res1 = await asyncio.gather(self.__opt(), self.__opt())
        assert res0 == res1 == 42

        # 单检操作
        assert 42 == await self.__opt()
        pass
    pass
