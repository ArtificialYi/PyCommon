import asyncio
import pytest
import sys

from asyncio import Future

from ..timeout import PytestAsyncTimeout

from ...src.tool.base import AsyncBase, BaseTool, DelayCountQueue


class TestBaseTool:
    def test_return_self(self):
        # 返回本身没有变化
        int_a = 5
        int_b = BaseTool.return_self(int_a)
        assert id(int_a) == id(int_b)
        pass

    def test_all_none_iter(self):
        # 全是常规数值，不通过
        assert not BaseTool.all_none_iter([1, 2, 3, 4])

        # 存在None，不通过
        assert not BaseTool.all_none_iter([None, 2, 3, 4])

        # 全是0，不通过
        assert not BaseTool.all_none_iter([0, 0, 0, 0])

        # 全是False，不通过
        assert not BaseTool.all_none_iter([False, False, False, False])

        # 全是None，通过
        assert BaseTool.all_none_iter([None, None, None, None])
        pass

    def test_int(self):
        assert not BaseTool.isint(None)
        assert not BaseTool.isint(0.1)
        assert not BaseTool.isint([])
        assert not BaseTool.isint({})
        assert not BaseTool.isint('5')

        # 仅数字可以通过
        assert BaseTool.isint(5)
        assert BaseTool.isint(0)
        pass

    def test_true(self):
        assert not BaseTool.istrue(1)
        assert not BaseTool.istrue(False)

        # 仅bool类型的true可以通过
        assert BaseTool.istrue(True)
        pass

    def test_to_str(self):
        # 字符串不会有任何变化
        str_a = '1234'
        str_b = BaseTool.to_str(str_a)
        assert id(str_a) == id(str_b)

        # 数值型会被转为字符串
        int_c = int(str_a)
        str_d = BaseTool.to_str(int_c)
        # 会生成新的对象
        assert id(int_c) != id(str_d)
        # 内容相同，但是引用不同
        assert str_a == str_d
        assert id(str_a) != id(str_d)
        pass

    def test_is_none(self):
        assert BaseTool.isnone(None)
        assert not BaseTool.isnone(1)
        pass
    pass


class TestDelayCountQueue:
    def test_average(self):
        # 队列：[0]
        queue_a = DelayCountQueue(0, max_len=2)
        assert queue_a.average == 0

        # 队列：[0, 2]
        queue_a.newest = 2
        assert abs(queue_a.average - 1) < 1e-4
        assert queue_a.newest == 2

        # 队列：[2, 4],队列最大长度为2
        queue_a.newest = 4
        assert abs(queue_a.average - 3) < 1e-4
        pass
    pass


class TestAsyncBase:
    @PytestAsyncTimeout(1)
    async def test_future_one(self):
        """future在单流程效果
        """
        res_a = 123
        future = AsyncBase.get_future()
        future.set_result(res_a)
        res_b = await future
        assert res_a == res_b
        assert id(res_a) == id(res_b)
        pass

    async def afuture_set(self, future: Future, res):
        await asyncio.sleep(1)
        future.set_result(res)
        return res

    @PytestAsyncTimeout(2)
    async def test_future_multi(self):
        """future在多协程效果
        action:
            1. 第一个协程创建future & await future & 关闭协程
            2. 第二个协程等待一段时间后set_result & 关闭协程
        except: 顺利关闭
        """
        res_a = 123
        future = AsyncBase.get_future()
        # 耗时1秒
        res_b, res_c = await asyncio.gather(future, self.afuture_set(future, res_a))
        assert res_a == res_b == res_c
        assert id(res_a) == id(res_b) == id(res_c)
        pass

    @PytestAsyncTimeout(2)
    async def test_add_cor_no_res(self):
        """
        1. 测试添加一个不需要返回值的coro
        2. 测试有返回值的coro的返回值
        """
        # 测试添加一个不需要返回值的coro
        res_a = 123
        future = AsyncBase.get_future()
        # 耗时1秒
        task = asyncio.create_task(self.afuture_set(future, res_a))
        res_b = await future
        res_c = await task
        assert res_a == res_b == res_c
        assert id(res_a) == id(res_b) == id(res_c)
        pass

    def iter_future_set(self, future: Future, res):
        future.set_result(res)
        yield
        return res

    @PytestAsyncTimeout(1)
    @pytest.mark.skipif(sys.version_info >= (3, 12), reason="py312以上版本不支持生成器直接转为协程")
    async def test_sync2async(self):
        """当前行为在python3.12以上版本会报错
        """
        res_a = 123
        future = AsyncBase.get_future()
        task = asyncio.create_task(self.iter_future_set(future, res_a))
        res_b = await future
        res_c = await task
        assert res_a == res_b == res_c
        assert id(res_a) == id(res_b) == id(res_c)
        pass
    pass
