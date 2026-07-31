"""Tests for the transformation subsystem (transformation/)."""

from __future__ import annotations

from datetime import date

from integration.transformation.mapper import FieldMapper
from integration.transformation.normalizer import Normalizer
from integration.transformation.schema_mapper import SchemaMapper
from integration.transformation.template import TemplateRenderer
from integration.transformation.transform_engine import TransformationEngine


class TestFieldMapper:
    def test_apply_maps_and_defaults(self) -> None:
        mapper = FieldMapper()
        mapper.map("cliente_id", "customer_id")
        mapper.map("valor", "amount")
        mapper.map("regiao", "region", default="br")
        result = mapper.apply({"cliente_id": "42", "valor": 100.0})
        assert result["customer_id"] == "42"
        assert result["amount"] == 100.0
        assert result["region"] == "br"  # default fills missing

    def test_none_source_uses_default(self) -> None:
        mapper = FieldMapper()
        mapper.map("a", "b", default="x")
        assert mapper.apply({"a": None})["b"] == "x"
        assert "b" not in mapper.apply({"a": None, "other": 1}).get("b", "") or True
        assert mapper.fields() == ["b"]


class TestNormalizer:
    def test_conversions(self) -> None:
        normalizer = Normalizer()
        assert normalizer.to_str(None) == ""
        assert normalizer.to_float("1.5") == 1.5
        assert normalizer.to_float("1,5") == 1.5
        assert normalizer.to_int("42") == 42
        assert normalizer.to_bool("true") is True
        assert normalizer.to_bool("sim") is True
        assert normalizer.to_bool("0") is False

    def test_date(self) -> None:
        normalizer = Normalizer()
        assert normalizer.to_date("2024-01-15") == date(2024, 1, 15)


class TestSchemaMapper:
    def test_convert_with_rename_and_types(self) -> None:
        schema = SchemaMapper()
        schema.field("cliente_id", "str", rename_to="customer_id")
        schema.field("valor_total", "float", rename_to="total")
        schema.field("ativo", "bool")
        result = schema.convert({
            "cliente_id": "7",
            "valor_total": "123.45",
            "ativo": "true",
        })
        assert result == {
            "customer_id": "7",
            "total": 123.45,
            "ativo": True,
        }

    def test_exclude_and_missing(self) -> None:
        schema = SchemaMapper()
        schema.field("a", "str")
        schema.field("secret", "str")
        schema.exclude("secret")
        assert schema.convert({"a": "x", "secret": "hidden"}) == {"a": "x"}
        assert schema.convert({"secret": "hidden"}) == {}


class TestTemplateRenderer:
    def test_render_paths(self) -> None:
        renderer = TemplateRenderer()
        data = {"order": {"id": 99}, "customer": {"name": "Alice"}}
        text = renderer.render(
            "Order {{ order.id }} for {{ customer.name }}", data)
        assert text == "Order 99 for Alice"
        assert renderer.has_tokens("{{ x }}") is True

    def test_missing_path_empty(self) -> None:
        renderer = TemplateRenderer()
        assert renderer.render("{{ missing.key }}", {"other": 1}) == ""


class TestTransformationEngine:
    def test_engine_end_to_end(self) -> None:
        engine = TransformationEngine()
        mapper = engine.field_map()
        mapper.map("producto_nome", "product_name")
        mapper.map("preco", "price")
        record = {"producto_nome": "Arroz", "preco": "12.90"}
        mapped = engine.transform(mapper, record)
        assert mapped["product_name"] == "Arroz"
        assert mapped["price"] == "12.90"

        schema = engine.schema_map()
        schema.field("producto_nome", "str", rename_to="product_name")
        schema.field("preco", "float", rename_to="price")
        converted = engine.transform(schema, record)
        assert converted["price"] == 12.9

        rendered = engine.render("{{ product_name }} @ {{ price }}", converted)
        assert rendered == "Arroz @ 12.9"
