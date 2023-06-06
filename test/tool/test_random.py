from ...src.tool.random_tool import RandomTool


class TestRandomTool:
    def test(self):
        for _ in range(1 << 6):
            assert 0 <= RandomTool.random() <= 1
        pass
    pass
