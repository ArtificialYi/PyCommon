import asyncio

from ...exception.db import UnsupportedSqlTypesError
from .sqlite import SqliteManage
from .rds import MysqlManage, RDSConfigData
from ....configuration.env import ConfigFetcher
from ...tool.base import BaseTool
from ...tool.map_tool import MapKey


class SqlManage:
    @staticmethod
    @MapKey(BaseTool.return_self)
    async def get_instance_by_tag(tag: str):
        sql_type = await ConfigFetcher.get_value_by_tag_and_field(tag, 'sql_type')
        if sql_type == 'mysql':
            return MysqlManage(RDSConfigData(*await asyncio.gather(*(
                ConfigFetcher.get_value_by_tag_and_field(tag, field)
                for field in RDSConfigData.FIELDS
            ))))
        elif sql_type == 'sqlite':
            return SqliteManage(await ConfigFetcher.get_value_by_tag_and_field(tag, 'db'))
        raise UnsupportedSqlTypesError(f'不支持的sql_type:{sql_type}')
    pass
