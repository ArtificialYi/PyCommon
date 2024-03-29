from attr import fields

from .rds import MysqlManageSync, RDSConfigData
from .sqlite import SqliteManageSync

from ...exception.db import UnsupportedSqlTypesError
from ...configuration.sync.env import get_value_by_tag_and_field


class SqlManageSync:
    @staticmethod
    def create(tag: str):
        sql_type = get_value_by_tag_and_field(tag, 'sql_type')
        match sql_type:
            case 'mysql':  # pragma: no cover
                return MysqlManageSync(RDSConfigData(*(
                    get_value_by_tag_and_field(tag, attr.name)
                    for attr in fields(RDSConfigData)
                )))
            case 'sqlite':
                return SqliteManageSync(get_value_by_tag_and_field(tag, 'db'))
            case _:  # pragma: no cover
                raise UnsupportedSqlTypesError(f'不支持的sql_type:{sql_type}')
    pass
