import os


class OSTool:
    @staticmethod
    def remove(path: str):
        """删除文件
        """
        try:
            os.remove(path)
        except FileNotFoundError:
            print(f'WARN:想删除的文件不存在:{path}')
            pass
        pass
    pass
