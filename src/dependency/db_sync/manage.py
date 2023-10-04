from attr import fields

from .rds import MysqlManageSync, RDSConfigData
from .sqlite import SqliteManageSync

from ...tool.base import BaseTool
from ...exception.db import UnsupportedSqlTypesError
from ...tool.map_tool import MapKey
from ...configuration.sync.env import get_value_by_tag_and_field


class SqlManageSync:
    @staticmethod
    @MapKey(BaseTool.return_self)
    def get_instance_by_tag(tag: str):
        sql_type = get_value_by_tag_and_field(tag, 'sql_type')
        if sql_type == 'mysql':
            return MysqlManageSync(RDSConfigData(*(
                get_value_by_tag_and_field(tag, attr.name)
                for attr in fields(RDSConfigData)
            )))
        elif sql_type == 'sqlite':
            return SqliteManageSync(get_value_by_tag_and_field(tag, 'db'))

        raise UnsupportedSqlTypesError(f'不支持的sql_type:{sql_type}')  # pragma: no cover
    pass
