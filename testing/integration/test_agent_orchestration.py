"""Testes de integração: Orquestração de Agentes."""

import pytest
from agents.planner.planner import Planner
from agents.execution.executor import Executor


class TestAgentOrchestration:
    """Testes de integração para orquestração de agentes."""

    @pytest.mark.asyncio
    async def test_planner_gera_steps(self):
        """Testa que o planner gera steps a partir de um objetivo."""
        planner = Planner()
        steps = await planner.plan("Criar uma API REST para gerenciar usuários")

        assert len(steps) > 0
        assert all(s.description for s in steps)
        assert all(s.assigned_agent for s in steps)

    @pytest.mark.asyncio
    async def test_planner_dependencias(self):
        """Testa que dependências entre steps estão corretas."""
        planner = Planner()
        steps = await planner.plan("Projeto completo com testes")

        # Steps iniciais não devem ter dependências
        initial_steps = [s for s in steps if not s.depends_on]
        assert len(initial_steps) > 0

        # Steps finais devem depender de anteriores
        final_steps = [s for s in steps if s.depends_on]
        assert len(final_steps) > 0

    @pytest.mark.asyncio
    async def test_planner_ready_steps(self):
        """Testa que ready steps retorna steps sem dependências pendentes."""
        planner = Planner()
        steps = await planner.plan("Projeto simples")

        ready = planner.get_ready_steps()
        assert len(ready) > 0

        # Marcar um como completo
        planner.mark_completed(steps[0].id)

        # Mais steps devem ficar prontos
        ready_after = planner.get_ready_steps()
        assert len(ready_after) >= len(ready)

    @pytest.mark.asyncio
    async def test_planner_clear(self):
        """Testa limpeza do planner."""
        planner = Planner()
        await planner.plan("Projeto")
        assert len(planner.get_steps()) > 0

        planner.clear()
        assert len(planner.get_steps()) == 0
