class Mysql2Other:
    @staticmethod
    def sqlite(sql: str):
        return sql.replace('%s', '?')
    pass
