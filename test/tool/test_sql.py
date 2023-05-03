import pytest
from ...src.tool.sql_tool import SQLTool


class TestSqlTool:
    def test_rule2name(self):
        assert SQLTool.rule2name("_lst.name_lst.age") == "_name_age"
        assert SQLTool.rule2name("name_lst.age") == "name_age"
        assert SQLTool.rule2name("name.age") == "name.age"
        assert SQLTool.rule2name("") == ""
        pass

    class DummyDBT:
        name_lst = ["John", "Doe"]
        age_lst = [30, 35]
        pass

    def test_rule2value(self):
        dbt = self.DummyDBT()

        assert SQLTool.rule2value(dbt, "name_lst.0") == "John"
        assert SQLTool.rule2value(dbt, "name_lst.1") == "Doe"
        assert SQLTool.rule2value(dbt, "age_lst.0") == 30
        assert SQLTool.rule2value(dbt, "age_lst.1") == 35

        with pytest.raises(AttributeError):
            SQLTool.rule2value(dbt, "nonexistent_lst.0")

        with pytest.raises(IndexError):
            SQLTool.rule2value(dbt, "name_lst.2")
        pass

    def test_to_sql_fields(self):
        assert SQLTool.to_sql_fields(["name", "age"]) == "`name`,`age`"
        assert SQLTool.to_sql_fields([]) == "``"
        assert SQLTool.to_sql_fields(["one_field"]) == "`one_field`"
        pass

    def test_to_sql_format(self):
        assert SQLTool.to_sql_format(["name", "age"]) == "%(name)s,%(age)s"
        assert SQLTool.to_sql_format([]) == ""
        assert SQLTool.to_sql_format(["one_field"]) == "%(one_field)s"
        pass
    pass
