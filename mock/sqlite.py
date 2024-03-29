from typing import AsyncGenerator, Generator

from ..src.tool.os_tool import OSTool

from ..src.dependency.db.base import ConnExecutor
from ..src.dependency.db_sync.base import ConnExecutorSync

from ..src.dependency.db.sqlite import SqliteManage
from ..src.dependency.db_sync.sqlite import SqliteManageSync

from ..src.tool.time_tool import TimeTool


class MockDB:
    def __init__(self, db_name: str):
        self.__local_name = TimeTool.file2local(db_name)
        self.__sql_manage = SqliteManage(self.__local_name)
        pass

    def __call__(self, use_transaction: bool = False) -> AsyncGenerator[ConnExecutor, None]:
        return self.__sql_manage(use_transaction)

    def __enter__(self) -> SqliteManage:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.__sql_manage
        OSTool.remove(self.__local_name)
        pass
    pass


class MockDBSync:
    def __init__(self, db_name: str):
        self.__local_name = TimeTool.file2local(db_name)
        self.__sql_manage = SqliteManageSync(self.__local_name)
        pass

    def __call__(self, use_transaction: bool = False) -> Generator[ConnExecutorSync, None, None]:
        return self.__sql_manage(use_transaction)

    def __enter__(self) -> SqliteManageSync:
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        del self.__sql_manage
        OSTool.remove(self.__local_name)
        pass
    pass
