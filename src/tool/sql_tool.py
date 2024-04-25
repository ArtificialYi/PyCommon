import re
from typing import List


class SQLTool:
    __FIELD_RE = re.compile(r'_lst\.')

    @classmethod
    def rule2name(cls, field_rule: str):
        """将field_rule转化为field_name
        1. 将rule中的_lst.转化为_
        """
        return cls.__FIELD_RE.sub('_', field_rule)

    @classmethod
    def rule2value(cls, dbt: object, field_rule: str):
        attr_lst = cls.__FIELD_RE.split(field_rule)
        value = getattr(dbt, attr_lst[0] if len(attr_lst) == 1 else f'{attr_lst[0]}_lst')
        for idx_str in attr_lst[1:]:
            value = value[int(idx_str)]
            pass
        return value

    @staticmethod
    def to_sql_fields(fields: List[str]):
        return ','.join(f'`{field}`' for field in fields)

    @staticmethod
    def to_sql_format(fields: List[str]):
        return ','.join(f'%({field})s' for field in fields)

    @staticmethod
    def to_sqlite(sql: str):
        return sql.replace('%s', '?')

    @staticmethod
    def to_mysql(sql: str):  # pragma: no cover
        return sql.replace('?', '%s')
    pass
