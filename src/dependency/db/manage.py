import asyncio
from attr import fields

from .rds import MysqlManage, RDSConfigData
from .sqlite import SqliteManage
from ...tool.base import BaseTool
from ...tool.map_tool import MapKey
from ...exception.db import UnsupportedSqlTypesError
from ...configuration.norm.env import get_value_by_tag_and_field


class SqlManage:
    @staticmethod
    @MapKey(BaseTool.return_self)
    async def get_instance_by_tag(tag: str):
        sql_type = await get_value_by_tag_and_field(tag, 'sql_type')
        if sql_type == 'mysql':
            return MysqlManage(RDSConfigData(*await asyncio.gather(*(
                get_value_by_tag_and_field(tag, attr.name)
                for attr in fields(RDSConfigData)
            ))))
        elif sql_type == 'sqlite':
            return SqliteManage(await get_value_by_tag_and_field(tag, 'db'))
        raise UnsupportedSqlTypesError(f'不支持的sql_type:{sql_type}')  # pragma: no cover
    pass
