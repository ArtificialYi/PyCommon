import os

from ...src.tool.os_tool import OSTool

from ...src.tool.time_tool import TimeTool


class TestOSTool:
    def test_exist(self):
        """文件存在情况下的删除
        """
        local_name = TimeTool.file2local('test_os.tmp')
        assert not os.path.exists(local_name)
        with open(local_name, 'w') as f:
            f.write('test')
            pass
        assert os.path.exists(local_name)
        OSTool.remove(local_name)
        assert not os.path.exists(local_name)
        pass

    def test_not_exist(self):
        """文件不存在情况下的删除
        """
        local_name = TimeTool.file2local('test_os.tmp')
        assert not os.path.exists(local_name)
        OSTool.remove(local_name)
        assert not os.path.exists(local_name)
        pass
    pass
