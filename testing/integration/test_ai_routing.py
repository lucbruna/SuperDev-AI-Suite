"""Testes de integração: AI Router com provedores."""

import pytest
from ai_platform.routing.smart_router import SmartAIRouter, SelectionStrategy, TaskType


class TestAIRoutingIntegration:
    """Testes de integração para o AI Router."""

    @pytest.fixture
    def router(self):
        return SmartAIRouter()

    def test_roteamento_por_qualidade(self, router):
        """Testa roteamento priorizando qualidade."""
        result = router.route(
            task_type=TaskType.CODE_GENERATION,
            strategy=SelectionStrategy.QUALITY_FIRST,
        )
        assert result is not None
        assert "model" in result

    def test_roteamento_por_custo(self, router):
        """Testa roteamento priorizando custo baixo."""
        result = router.route(
            task_type=TaskType.CODE_GENERATION,
            strategy=SelectionStrategy.COST_FIRST,
        )
        assert result is not None

    def test_roteamento_por_latencia(self, router):
        """Testa roteamento priorizando latência baixa."""
        result = router.route(
            task_type=TaskType.CODE_GENERATION,
            strategy=SelectionStrategy.LATENCY_FIRST,
        )
        assert result is not None

    def test_health_check_modelos(self, router):
        """Testa que health check funciona para modelos."""
        models = router.list_available_models()
        assert len(models) > 0

        # Atualizar health de um provedor
        router.update_health("openai", True)
        health = router.get_provider_health("openai")
        assert health is not None

    def test_fallback_provedor(self, router):
        """Testa fallback quando provedor está indisponível."""
        # Simular provedor indisponível
        router.update_health("openai", False)

        result = router.route(
            task_type=TaskType.CODE_GENERATION,
            strategy=SelectionStrategy.QUALITY_FIRST,
        )
        # Deve rotear para outro provedor
        assert result is not None
