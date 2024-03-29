import asyncio
from attr import fields

from .rds import MysqlManage, RDSConfigData
from .sqlite import SqliteManage

from ...exception.db import UnsupportedSqlTypesError
from ...configuration.norm.env import get_value_by_tag_and_field


class SqlManage:
    @staticmethod
    async def create(tag: str):
        sql_type = await get_value_by_tag_and_field(tag, 'sql_type')
        match sql_type:
            case 'mysql':  # pragma: no cover
                return MysqlManage(RDSConfigData(*await asyncio.gather(*(
                    get_value_by_tag_and_field(tag, attr.name)
                    for attr in fields(RDSConfigData)
                ))))
            case 'sqlite':
                return SqliteManage(await get_value_by_tag_and_field(tag, 'db'))
            case _:  # pragma: no cover
                raise UnsupportedSqlTypesError(f'不支持的sql_type:{sql_type}')
    pass
