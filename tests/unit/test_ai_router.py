"""Testes unitários para o SmartAIRouter."""

import pytest
from ai_platform.routing.smart_router import (
    SmartAIRouter,
    SelectionStrategy,
    TaskType,
)


class TestSmartAIRouter:
    """Testes para o SmartAIRouter."""

    @pytest.fixture
    def router(self):
        return SmartAIRouter()

    def test_inicializacao(self, router):
        assert router is not None
        assert len(router._models) > 0

    def test_estrategias(self):
        assert SelectionStrategy.COST_FIRST.value == "cost_first"
        assert SelectionStrategy.QUALITY_FIRST.value == "quality_first"
        assert SelectionStrategy.LATENCY_FIRST.value == "latency_first"
        assert SelectionStrategy.AUTO.value == "auto"

    def test_tipos_tarefa(self):
        assert TaskType.CODE_GENERATION.value == "code_generation"
        assert TaskType.CODE_REVIEW.value == "code_review"
        assert TaskType.TESTING.value == "testing"
        assert TaskType.DOCUMENTATION.value == "documentation"

    def test_modelos_disponiveis(self, router):
        models = router.list_available_models()
        assert len(models) > 0
        assert any("gpt" in m.lower() or "claude" in m.lower() for m in models)

    def test_health_check(self, router):
        router.update_health("openai", True)
        health = router.get_provider_health("openai")
        assert health is not None

    def test_rotas_por_estrategia(self, router):
        # Teste de roteamento por custo
        route = router.route(
            task_type=TaskType.CODE_GENERATION,
            strategy=SelectionStrategy.COST_FIRST,
        )
        assert route is not None
        assert "model" in route
