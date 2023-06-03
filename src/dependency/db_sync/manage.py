from ...configuration.sync.env import get_value_by_tag_and_field
from ...exception.db import UnsupportedSqlTypesError
from .rds import MysqlManageSync, RDSConfigData


class SqlManageSync:
    @staticmethod
    def get_instance_by_tag(tag: str):
        sql_type = get_value_by_tag_and_field(tag, 'sql_type')
        if sql_type == 'mysql':
            return MysqlManageSync(RDSConfigData(*(
                get_value_by_tag_and_field(tag, field)
                for field in RDSConfigData.FIELDS
            )))
        raise UnsupportedSqlTypesError(f'不支持的sql_type:{sql_type}')  # pragma: no cover
    pass
