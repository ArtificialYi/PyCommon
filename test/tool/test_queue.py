from ...src.tool.queue_tool import MovingAvg


class TestMovingAvg:
    def test_one(self):
        # 测试长度为1的情况
        moving = MovingAvg(1, 1.4)
        # 当前有效[1.4], 平均数为1.4，待构造为[x]
        assert moving.avg() == 1.4
        # 目标平均数为1，则只需要插入1
        assert moving.avg_target(1) == 1
        # 目标平均数为2，则只需要插入2
        assert moving.avg_target(2) == 2

        moving.push(1)
        assert moving.avg() == 1
        # 目标平均数为2，则只需要插入2
        assert moving.avg_target(2) == 2
        pass

    def test_two(self):
        # 测试长度为2的情况
        moving = MovingAvg(2, 0)
        # 初始化2个0，平均数为0
        assert moving.avg() == 0
        # 目标平均数为1，则需要构造[0, 2]
        assert moving.avg_target(1) == 2
        # 目标平均数为2，则需要构造[0, 4]
        assert moving.avg_target(2) == 4

        moving.push(2)
        # 当前有效[0, 2], 平均数为1，待构造为[2, x]
        assert moving.avg() == 1
        # 目标平均数为1，则需要构造[2, 0]
        assert moving.avg_target(1) == 0
        # 目标平均数为2，则需要构造[2, 2]
        assert moving.avg_target(2) == 2
    pass
