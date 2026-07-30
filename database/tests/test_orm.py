from __future__ import annotations

import pytest  # type: ignore[import-untyped]

from SuperDev.database.orm import Field, Model, QueryBuilder


class TestField:
    def test_descriptor(self) -> None:
        f = Field(data_type="integer", primary_key=True)
        assert f.metadata.data_type == "integer"
        assert f.metadata.primary_key is True

    def test_default_values(self) -> None:
        f = Field()
        assert f.metadata.data_type == "text"
        assert f.metadata.nullable is True

    def test_unique_constraint(self) -> None:
        f = Field(data_type="varchar", unique=True)
        assert f.metadata.unique is True


class TestModel:
    def test_auto_table_name(self) -> None:
        class Product(Model):
            id = Field(primary_key=True)
            name = Field()

        assert Product._table == "product"

    def test_custom_table_name(self) -> None:
        class User(Model):
            __table__ = "users"
            id = Field(primary_key=True)

        assert User._table == "users"

    def test_fields_collected(self) -> None:
        class Item(Model):
            id = Field(primary_key=True)
            sku = Field(data_type="varchar")
            price = Field(data_type="float")

        assert "id" in Item._fields
        assert "sku" in Item._fields
        assert "price" in Item._fields
        assert len(Item._fields) == 3

    def test_inheritance(self) -> None:
        class Base(Model):
            id = Field(primary_key=True)
            created_at = Field(data_type="timestamp")

        class Extended(Base):
            name = Field()

        assert "id" in Extended._fields
        assert "created_at" in Extended._fields
        assert "name" in Extended._fields

    def test_pk_value(self) -> None:
        class Order(Model):
            id = Field(primary_key=True)
            total = Field(data_type="float")

        o = Order(id=42, total=99.99)
        assert o.pk_value() == 42
        assert o.pk_name() == "id"

    def test_to_dict(self) -> None:
        class Tag(Model):
            name = Field()

        t = Tag(name="urgent")
        assert t.to_dict() == {"name": "urgent"}

    def test_from_dict(self) -> None:
        class Category(Model):
            code = Field()

        c = Category.from_dict({"code": "A1"})
        assert c._values["code"] == "A1"

    def test_repr(self) -> None:
        class Status(Model):
            code = Field()

        s = Status(code="active")
        r = repr(s)
        assert "Status" in r
        assert "active" in r

    def test_field_access(self) -> None:
        class Person(Model):
            name = Field()

        p = Person(name="Alice")
        assert p.name == "Alice"
        p.name = "Bob"
        assert p.name == "Bob"


class TestQueryBuilder:
    def test_select_all(self) -> None:
        qb = QueryBuilder(dialect="postgresql")
        sql, params = qb.select("*").from_table("users").build()
        assert "SELECT *" in sql
        assert '"users"' in sql

    def test_select_with_where(self) -> None:
        qb = QueryBuilder()
        sql, params = qb.select("id", "name").from_table("users").where("id = %s", 1).build()
        assert sql.startswith("SELECT")
        assert params == [1]

    def test_insert(self) -> None:
        qb = QueryBuilder(dialect="sqlite")
        sql, params = qb.insert("users").set_values({"name": "Alice", "age": 30}).build()
        assert "INSERT INTO" in sql
        assert params == ["Alice", 30]

    def test_insert_returning(self) -> None:
        qb = QueryBuilder(dialect="postgresql")
        sql, params = qb.insert("users").set_values({"name": "Bob"}).returning("id").build()
        assert "RETURNING" in sql
        assert "id" in sql

    def test_update(self) -> None:
        qb = QueryBuilder(dialect="mysql")
        sql, params = qb.update("users").set_values({"name": "Bob"}).where("id = ?", 1).build()
        assert "UPDATE" in sql
        assert params == ["Bob", 1]

    def test_delete(self) -> None:
        qb = QueryBuilder()
        sql, params = qb.delete("users").where("id = %s", 5).build()
        assert "DELETE" in sql
        assert params == [5]

    def test_order_by(self) -> None:
        qb = QueryBuilder()
        sql, _ = qb.select("*").from_table("t").order_by("name", "DESC").build()
        assert "ORDER BY" in sql
        assert "DESC" in sql

    def test_limit_offset(self) -> None:
        qb = QueryBuilder()
        sql, _ = qb.select("*").from_table("t").limit(10).offset(20).build()
        assert "LIMIT 10" in sql
        assert "OFFSET 20" in sql

    def test_join(self) -> None:
        qb = QueryBuilder()
        sql, _ = qb.select("*").from_table("users").join("orders", "users.id = orders.user_id").build()
        assert "JOIN" in sql

    def test_reset(self) -> None:
        qb = QueryBuilder()
        qb.select("*").from_table("users")
        qb.reset()
        sql, params = qb.select("id").from_table("items").build()
        assert "items" in sql

    def test_dialect_quoting_postgres(self) -> None:
        qb = QueryBuilder(dialect="postgresql")
        sql, _ = qb.select("*").from_table("user").build()
        assert '"user"' in sql

    def test_dialect_quoting_mysql(self) -> None:
        qb = QueryBuilder(dialect="mysql")
        sql, _ = qb.select("*").from_table("user").build()
        assert "`user`" in sql

    def test_dialect_quoting_mssql(self) -> None:
        qb = QueryBuilder(dialect="sqlserver")
        sql, _ = qb.select("*").from_table("user").build()
        assert "[user]" in sql
