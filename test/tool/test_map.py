import asyncio

from ..timeout import PytestAsyncTimeout

from ...src.tool.base import BaseTool
from ...src.tool.map_tool import MapKeyGlobal, MapKeySelf


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

    @MapKeySelf()
    def func_self_no_key(self):
        return object()

    @MapKeySelf()
    async def func_aself_no_key(self):
        await asyncio.sleep(0.1)
        return object()

    @MapKeySelf(lambda _, key: key)
    async def func_aself_norm(self, key):
        await asyncio.sleep(0.1)
        return object()
    pass


class TestMapKeyGlobal:
    def test_base(self):
        """基础测试
        """
        assert id(MapKeyTmp.func_norm()) != id(MapKeyTmp.func_norm())

    def test_norm_no_key(self):
        """MapKeyGlobal普通函数无Key测试
        """
        assert id(MapKeyTmp.func_norm_no_key()) == id(MapKeyTmp.func_norm_no_key())
        pass

    @PytestAsyncTimeout(1)
    async def test_async_no_key(self):
        """MapKey异步函数无Key测试
        """
        res0, res1 = await asyncio.gather(MapKeyTmp.func_async_no_key(), MapKeyTmp.func_async_no_key())
        res2 = await MapKeyTmp.func_async_no_key()
        assert id(res0) == id(res1) == id(res2)
        pass

    @PytestAsyncTimeout(1)
    async def test_async_norm(self):
        """MapKey异步函数有Key测试
        """
        res0 = await MapKeyTmp.func_async_norm(1)
        res1 = await MapKeyTmp.func_async_norm(2)
        res2 = await MapKeyTmp.func_async_norm(1)
        assert id(res1) != id(res0) == id(res2)
        pass
    pass


class TestMapKeySelf:
    def test_self_no_key(self):
        """MapKeySelf普通函数无Key测试"""
        tmp0 = MapKeyTmp()
        obj0 = tmp0.func_self_no_key()
        obj1 = tmp0.func_self_no_key()

        tmp1 = MapKeyTmp()
        obj2 = tmp1.func_self_no_key()
        assert id(obj0) == id(obj1) != id(obj2)
        pass

    @PytestAsyncTimeout(1)
    async def test_aself_no_key(self):
        """MapKeySelf异步函数无Key测试"""
        tmp0 = MapKeyTmp()
        obj0, obj1 = await asyncio.gather(tmp0.func_aself_no_key(), tmp0.func_aself_no_key())
        obj2 = await tmp0.func_aself_no_key()

        tmp1 = MapKeyTmp()
        obj3 = await tmp1.func_aself_no_key()
        assert id(obj0) == id(obj1) == id(obj2) != id(obj3)
        pass

    @PytestAsyncTimeout(1)
    async def test_aself_norm(self):
        """MapKeySelf异步函数有Key测试"""
        tmp0 = MapKeyTmp()
        obj0, obj1, obj2 = await asyncio.gather(tmp0.func_aself_norm(1), tmp0.func_aself_norm(1), tmp0.func_aself_norm(2))
        assert id(obj0) == id(obj1) != id(obj2)
        pass
    pass
