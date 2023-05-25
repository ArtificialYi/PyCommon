import asyncio

from ....configuration.env import get_value_by_tag_and_field
from ...exception.db import UnsupportedSqlTypesError
from .sqlite import SqliteManage
from .rds import MysqlManage, RDSConfigData


class SqlManage:
    @staticmethod
    async def get_instance_by_tag(tag: str):
        sql_type = await get_value_by_tag_and_field(tag, 'sql_type')
        if sql_type == 'mysql':
            return MysqlManage(RDSConfigData(*await asyncio.gather(*(
                get_value_by_tag_and_field(tag, field)
                for field in RDSConfigData.FIELDS
            ))))
        elif sql_type == 'sqlite':
            return SqliteManage(await get_value_by_tag_and_field(tag, 'db'))
        raise UnsupportedSqlTypesError(f'不支持的sql_type:{sql_type}')  # pragma: no cover
    pass
