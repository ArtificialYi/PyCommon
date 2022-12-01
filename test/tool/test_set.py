from ...src.tool.set_tool import SetTargetManage


class TestSetTargetManage:
    def test(self):
        # 无目标对象
        set_manage = SetTargetManage()

        # 由于无目标，无法添加新对象
        set_manage.add(0)
        assert len(set_manage.added_set) == 0

        # 设置目标后可以添加
        set_manage.set_target(set(range(5)))
        assert len(set_manage.added_set) == 0
        set_manage.add(1)
        assert len(set_manage.added_set) == 1

        # 查看尚未添加目标，不会影响已添加和目标
        assert len(set_manage.not_added_set) == 4
        assert set_manage.not_added_one in [0, 2, 3, 4]
        assert len(set_manage.not_added_set) == 4
        pass
    pass
