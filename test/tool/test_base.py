from ...src.tool.base import BaseTool


class TestBaseTool:
    def test_return_self(self):
        # 返回本身没有变化
        tmp = 5
        a_id = id(tmp)
        b_id = id(BaseTool.return_self(tmp))
        assert a_id == b_id
        pass

    def test_all_none_iter(self):
        # 全是常规数值，无法通过
        tmp_a = [1, 2, 3, 4]
        assert not BaseTool.all_none_iter(tmp_a)

        # 存在None，无法通过
        tmp_b = [1, 2, 3, None]
        assert not BaseTool.all_none_iter(tmp_b)

        # 全是None，通过
        tmp_c = [None, None, None, None]
        assert BaseTool.all_none_iter(tmp_c)

        # 全是0，不通过
        tmp_d = [0, 0, 0, 0]
        assert not BaseTool.all_none_iter(tmp_d)

        # 全是False，不通过
        tmp_e = [False, False, False, False]
        assert not BaseTool.all_none_iter(tmp_e)
        pass
    pass
