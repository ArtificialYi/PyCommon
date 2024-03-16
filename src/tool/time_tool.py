import time
import uuid


class TimeTool:
    @staticmethod
    def __get_format_with_uuid(format: str):
        return f'{time.strftime(format)}.{uuid.uuid4()}'

    @staticmethod
    def file2local(file_name: str, format: str = '%Y%m%d-%H%M%S'):
        time_tmp = TimeTool.__get_format_with_uuid(format)
        return f'{time_tmp}.{file_name}'
    pass
