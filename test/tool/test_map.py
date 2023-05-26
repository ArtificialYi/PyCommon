import asyncio

from ..timeout import PytestAsyncTimeout
from ...src.tool.map_tool import MapKey


class TestMapKey:
    @MapKey()
    def __func_norm_no_key(self):
        return object()

    @MapKey()
    async def __func_async_no_key(self):
        await asyncio.sleep(0.1)
        return object()

    def __key_norm(self):
        return self

    @MapKey(__key_norm)
    async def __func_async_norm(self):
        await asyncio.sleep(0.1)
        return object()

    def test_base(self):
        assert id(object()) != id(object())

    def test_norm_no_key(self):
        res0 = self.__func_norm_no_key()
        res1 = self.__func_norm_no_key()
        assert id(res0) == id(res1)
        pass

    @PytestAsyncTimeout(1)
    async def test_async_no_key(self):
        res0, res1 = await asyncio.gather(self.__func_async_no_key(), self.__func_async_no_key())
        res2 = await self.__func_async_no_key()
        assert id(res0) == id(res1) == id(res2)
        pass

    @PytestAsyncTimeout(1)
    async def test_async_norm(self):
        res0 = await self.__func_async_norm()
        res1 = await self.__func_async_norm()
        assert id(res0) == id(res1)
        pass
    pass
