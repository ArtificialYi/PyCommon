import sqlite3
from typing import Generator
import pytest

from ...src.dependency.db.manage import SqlManage

from ...src.exception.db import MultipleResultsFound

from ...mock.sqlite import MockDB

from ..timeout import PytestAsyncTimeout
from ...src.dependency.db.sqlite import ServiceNorm, SqliteManage


class TestSqliteManage:
    async def __sql_exec(self, sql_manage: SqliteManage, sql: str, args: tuple):
        async with sql_manage(True) as conn:
            return await conn.exec(sql, args)
        pass

    @PytestAsyncTimeout(1)
    async def test_db_create(self):
        with MockDB('test.db') as sql_manage:
            assert isinstance(sql_manage, MockDB)
            assert not await ServiceNorm.table_exist(sql_manage, 'test')
            pass

        with pytest.raises(AttributeError):
            await ServiceNorm.table_exist(sql_manage, 'test')
        pass

    @pytest.fixture
    def db_create(self) -> Generator[SqliteManage, None, None]:
        with MockDB('test.db') as sql_manage:
            yield sql_manage
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_table_create(self, db_create: SqliteManage):
        table_name = 'test_table'
        sql = f"""
CREATE TABLE "main"."{table_name}" (
    "id" integer NOT NULL PRIMARY KEY AUTOINCREMENT
);
        """

        assert not await ServiceNorm.table_exist(db_create, table_name)
        assert await self.__sql_exec(db_create, sql, []) == -1
        assert await ServiceNorm.table_exist(db_create, table_name)

        with pytest.raises(sqlite3.OperationalError):
            assert await self.__sql_exec(db_create, sql, []) == -1
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_sql_type(self, db_create: SqliteManage):
        async with db_create() as conn:
            assert conn.sql_type == 'sqlite'
            pass
        pass

    @pytest.fixture
    async def sql_manage(self) -> SqliteManage:
        return await SqlManage.create('db-test')

    @PytestAsyncTimeout(1)
    async def test_iter(self, sql_manage: SqliteManage):
        async with sql_manage() as conn:
            async for row in conn.iter('SELECT 1;', ()):
                assert row == {'1': 1}
                pass
            pass
        pass

    @PytestAsyncTimeout(1)
    async def test_row_one_err(self, sql_manage: SqliteManage):
        async with sql_manage() as conn:
            with pytest.raises(MultipleResultsFound):
                await conn.row_one('SELECT 1 UNION SELECT 2;', ())
                pass
            pass
        pass
    pass
