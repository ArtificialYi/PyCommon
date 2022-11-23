from ...src.tool.statistics_tool import StatisticsContainer


class TestStatisticsContainer:
    def test(self):
        """测试统计模型基础功能
        1. 构造基础对象
        """
        a = StatisticsContainer()
        assert a.count == 0
        assert a.sum == 0
        assert a.avg == 0
        assert a.var == 0
        assert a.std == 0

        a.add(5)
        assert a.count == 1
        assert a.sum == 5
        assert a.avg == 5
        assert a.var == 0
        assert a.std == 0

        a.add(10)
        assert a.count == 2
        assert a.sum == 15
        assert a.avg == 7.5
        assert a.var == 12.5
        assert a.std == 12.5 ** 0.5
        pass
    pass
