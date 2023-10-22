import asyncio

from ..timeout import PytestAsyncTimeout

from ...src.tool.base import BaseTool
from ...src.tool.map_tool import MapKeyGlobal


class MapKeyTmp:
    @staticmethod
    @MapKeyGlobal()
    def func_norm_no_key():
        return object()

    @staticmethod
    @MapKeyGlobal()
    async def func_async_no_key():
        await asyncio.sleep(0.1)
        return object()

    @staticmethod
    @MapKeyGlobal(BaseTool.return_self)
    async def func_async_norm(key):
        await asyncio.sleep(0.1)
        return object()

    @staticmethod
    def func_norm():
        return object()
    pass


class TestMapKeyGlobal:
    def test_base(self):
        assert id(MapKeyTmp.func_norm()) != id(MapKeyTmp.func_norm())

    def test_norm_no_key(self):
        assert id(MapKeyTmp.func_norm_no_key()) == id(MapKeyTmp.func_norm_no_key())
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
