"""Tests for the templates subsystem (Volume 20, Fase 6)."""

from __future__ import annotations

import pytest

from automation.automation_models import WorkflowDefinition
from automation.templates.template_builder import TemplateBuilder
from automation.templates.template_engine import TemplateEngine
from automation.templates.template_history import TemplateHistory
from automation.templates.template_models import TemplateParameter, WorkflowTemplate
from automation.templates.template_renderer import TemplateRenderer
from automation.templates.template_validator import TemplateValidator


class TestTemplateModels:
    def test_parameter_defaults(self) -> None:
        param = TemplateParameter(name="url", required=True)
        assert param.required is True
        assert param.to_dict()["name"] == "url"

    def test_template_to_dict(self) -> None:
        template = WorkflowTemplate(template_id="t-1", name="Um",
                                    steps=[{"stage_id": "a", "action": "x"}])
        data = template.to_dict()
        assert data["steps"] == [{"stage_id": "a", "action": "x"}]
        assert data["category"] == "general"


class TestTemplateBuilder:
    def test_build(self) -> None:
        template = (TemplateBuilder()
                    .id("t-pedido").name("Pedido").category("business")
                    .step("enviar", "email.send", {"to": "{{email}}"})
                    .parameter("email", required=True)
                    .build())
        assert template.template_id == "t-pedido"
        assert len(template.steps) == 1
        assert template.parameters[0].name == "email"
        assert template.parameters[0].required is True


class TestTemplateValidator:
    def _valid(self) -> WorkflowTemplate:
        return (TemplateBuilder()
                .id("t-1").name("Válida")
                .step("a", "action.a", {"url": "{{url}}"})
                .parameter("url", required=True)
                .build())

    def test_valid(self) -> None:
        assert TemplateValidator().validate(self._valid()) == []

    def test_undeclared_placeholder(self) -> None:
        template = (TemplateBuilder()
                    .id("t-2").name("Indeclarado")
                    .step("a", "action.a", {"url": "{{url}}"})
                    .build())
        issues = TemplateValidator().validate(template)
        assert any("'url'" in i and "not declared" in i for i in issues)

    def test_missing_required_fields(self) -> None:
        template = TemplateBuilder().build()
        issues = TemplateValidator().validate(template)
        assert "template_id is required" in issues
        assert "name is required" in issues
        assert "template has no steps" in issues

    def test_stage_requires_action(self) -> None:
        template = (TemplateBuilder()
                    .id("t-3").name("Sem ação")
                    .step("a", "")
                    .build())
        assert any("action" in i for i in TemplateValidator().validate(template))


class TestTemplateRenderer:
    def test_substitute_action_and_params(self) -> None:
        renderer = TemplateRenderer()
        steps = [{"stage_id": "s1",
                  "action": "api.{{verb}}",
                  "params": {"url": "{{url}}", "nested": {"sku": "{{sku}}"}}}]
        rendered = renderer.render(steps, {"verb": "call", "url": "https://x",
                                           "sku": "arroz"})
        assert rendered[0]["action"] == "api.call"
        assert rendered[0]["params"]["url"] == "https://x"
        assert rendered[0]["params"]["nested"]["sku"] == "arroz"

    def test_unknown_placeholder_left_intact(self) -> None:
        assert TemplateRenderer().substitute("{{ghost}} aqui", {}) == "{{ghost}} aqui"


class TestTemplateEngine:
    def test_register_and_instantiate(self) -> None:
        engine = TemplateEngine()
        template = (engine.build()
                    .id("t-alerta").name("Alerta de estoque")
                    .category("business")
                    .step("notificar", "email.send", {"to": "{{email}}"})
                    .step("registrar", "log.write", {"level": "info"})
                    .parameter("email", required=True)
                    .build())
        assert engine.register(template) is None
        assert engine.list() == ["t-alerta"]
        definition = engine.instantiate("t-alerta", {"email": "loja@x.com"})
        assert definition is not None
        assert isinstance(definition, WorkflowDefinition)
        assert definition.workflow_id == "t-alerta"
        assert definition.steps[0].params["to"] == "loja@x.com"
        assert len(engine.usage()) == 1

    def test_missing_required_raises(self) -> None:
        engine = TemplateEngine()
        template = (engine.build()
                    .id("t-req").name("Obrigatório")
                    .step("a", "action.a", {"v": "{{v}}"})
                    .parameter("v", required=True)
                    .build())
        engine.register(template)
        with pytest.raises(ValueError, match="missing required"):
            engine.instantiate("t-req", {})
        assert engine.usage()[0]["ok"] is False

    def test_default_filled(self) -> None:
        engine = TemplateEngine()
        template = (engine.build()
                    .id("t-def").name("Default")
                    .step("a", "action.a", {"region": "{{region}}"})
                    .parameter("region", default="br")
                    .build())
        engine.register(template)
        definition = engine.instantiate("t-def", {})
        assert definition is not None
        assert definition.steps[0].params["region"] == "br"

    def test_unknown_template(self) -> None:
        assert TemplateEngine().instantiate("ghost", {}) is None

    def test_invalid_template_rejected(self) -> None:
        engine = TemplateEngine()
        template = (engine.build()
                    .id("t-bad").name("Ruim")
                    .step("a", "action.a", {"v": "{{v}}"})
                    .build())
        issues = engine.register(template)
        assert issues is not None
        assert any("not declared" in i for i in issues)

    def test_remove(self) -> None:
        engine = TemplateEngine()
        template = (engine.build().id("t-rm").name("Remover")
                    .step("a", "action.a")
                    .build())
        engine.register(template)
        assert engine.remove("t-rm") is True
        assert engine.remove("t-rm") is False

    def test_user_example_dev_workflow(self) -> None:
        """Exemplo real: workflow de desenvolvimento.

        Nova solicitação -> Planner cria tarefas -> Developer cria código ->
        Testing valida -> Security verifica -> DevOps publica.
        """
        engine = TemplateEngine()
        template = (engine.build()
                    .id("tpl-dev-workflow").name("Workflow de desenvolvimento")
                    .description("Pipeline de desenvolvimento com agentes")
                    .category("developer")
                    .step("planner", "agent.run",
                          {"agent": "planner", "task": "{{solicitacao}}"},
                          next_on_success="developer")
                    .step("developer", "agent.run",
                          {"agent": "developer"},
                          next_on_success="testing")
                    .step("testing", "agent.run",
                          {"agent": "testing"}, next_on_success="security")
                    .step("security", "agent.run",
                          {"agent": "security"}, next_on_success="devops")
                    .step("devops", "agent.run",
                          {"agent": "devops", "deploy": True})
                    .parameter("solicitacao", required=True,
                               description="Descrição da nova solicitação")
                    .build())
        assert engine.register(template) is None
        definition = engine.instantiate("tpl-dev-workflow",
                                        {"solicitacao": "Implementar login"})
        assert definition is not None
        actions = [step.action for step in definition.steps]
        assert actions == ["agent.run"] * 5
        assert definition.steps[0].params["task"] == "Implementar login"
        assert [s.next_on_success for s in definition.steps] == [
            "developer", "testing", "security", "devops", None]


class TestTemplateHistory:
    def test_count_filters(self) -> None:
        history = TemplateHistory()
        history.record("t-1", {"a": 1}, ok=True)
        history.record("t-1", {"a": 2}, ok=False,
                       error="boom")
        history.record("t-2", {"b": 3}, ok=True)
        assert history.count() == 3
        assert history.count("t-1") == 2
        assert history.count(ok=True) == 2
        assert history.count(ok=False) == 1
