import sqlite3
from typing import Generator
import pytest

from ...src.exception.db import MultipleResultsFound

from ...src.dependency.db_sync.manage import SqlManageSync
from ...src.dependency.db_sync.sqlite import ServiceNorm, SqliteManageSync
from ...mock.sqlite import MockDBSync


class TestSqliteManageSync:
    def test_db_create(self):
        with MockDBSync('test.db') as sql_manage:
            assert isinstance(sql_manage, MockDBSync)
            assert not ServiceNorm.table_exist(sql_manage, 'test')
            pass

        with pytest.raises(AttributeError):
            ServiceNorm.table_exist(sql_manage, 'test')
        pass

    @pytest.fixture
    def db_create(self) -> Generator[SqliteManageSync, None, None]:
        with MockDBSync('test.db') as sql_manage:
            yield sql_manage
            pass
        pass

    def test_table_create(self, db_create: SqliteManageSync):
        table_name = 'test_table'
        sql = f"""
CREATE TABLE "main"."{table_name}" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT
);
        """

        assert not ServiceNorm.table_exist(db_create, table_name)
        with db_create(True) as conn:
            assert conn.exec(sql, []) == -1
            pass
        assert ServiceNorm.table_exist(db_create, table_name)

        with pytest.raises(sqlite3.OperationalError):
            with db_create(True) as conn:
                conn.exec(sql, []) == -1
                pass
            pass
        pass

    def test_sql_type(self, db_create: SqliteManageSync):
        with db_create() as conn:
            assert conn.sql_type == 'sqlite'
            pass
        pass

    @pytest.fixture
    def sql_manage(self) -> SqliteManageSync:
        return SqlManageSync.create('db-test')

    def test_iter(self, sql_manage: SqliteManageSync):
        with sql_manage() as conn:
            for row in conn.iter('select * from zijin_feature limit 1;', ()):
                assert 'report_date' in row
                pass
            pass
        pass

    def test_row_one_err(self, sql_manage: SqliteManageSync):
        with sql_manage() as conn:
            with pytest.raises(MultipleResultsFound):
                conn.row_one('select * from zijin_feature;', ())
                pass
            pass
        pass
    pass
