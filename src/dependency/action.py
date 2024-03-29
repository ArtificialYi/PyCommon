class ActionNorm:
    @staticmethod
    def table_exist(table_name: str) -> tuple[str, tuple]:
        sql = """
SELECT COUNT(1) as COUNT FROM sqlite_master WHERE type='table' AND name=?;
"""
        return sql, (table_name,)
    pass
