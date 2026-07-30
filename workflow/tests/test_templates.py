from __future__ import annotations

from workflow.templates.template_models import Template
from workflow.templates.template_renderer import TemplateRenderer
from workflow.templates.template_cache import TemplateCache
from workflow.templates.template_validator import TemplateValidator
from workflow.templates.template_variables import TemplateVariables


class TestTemplates:
    def test_template_models(self) -> None:
        t = Template(name="test", content="Hello {{name}}", variables=["name"])
        assert t.name == "test"
        assert "{{name}}" in t.content

    def test_template_renderer(self) -> None:
        renderer = TemplateRenderer()
        result = renderer.render("Hello {{name}}", {"name": "World"})
        assert result == "Hello World"

    def test_template_renderer_missing_var(self) -> None:
        renderer = TemplateRenderer()
        result = renderer.render("Hello {{name}}", {})
        assert result == "Hello {{name}}"

    def test_template_cache(self) -> None:
        cache = TemplateCache()
        cache.set("t1", {"x": "y"}, "result")
        cached = cache.get("t1", {"x": "y"})
        assert cached == "result"

    def test_template_validator(self) -> None:
        validator = TemplateValidator()
        t = Template(name="test", content="Hello {{name}}", variables=["name"])
        assert validator.validate(t)
        t2 = Template(name="test", content="Hello {{missing}}", variables=["name"])
        assert not validator.validate(t2)

    def test_template_variables(self) -> None:
        tv = TemplateVariables({"name": "World"})
        result = tv.resolve("Hello {{name}}")
        assert result == "Hello World"
