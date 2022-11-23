from ...src.tool.base import BaseTool


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
        assert not BaseTool.all_none_iter([1, 2, 3, None])

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
        ## 会生成新的对象
        assert id(int_c) != id(str_d)
        ## 内容相同，但是引用不同
        assert str_a == str_d
        assert id(str_a) != id(str_d)
        pass
    pass
