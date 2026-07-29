"""Testes unitários para o Planner."""

import pytest
import json
from unittest.mock import AsyncMock, MagicMock
from agents.planner.planner import Planner, Step


class MockLLMProvider:
    """Mock de provedor LLM para testes."""

    def __init__(self, response: str = ""):
        self._response = response
        self.calls: list[dict] = []

    async def complete(self, messages: list[dict[str, str]], model: str = "") -> str:
        self.calls.append({"messages": messages, "model": model})
        return self._response


class TestPlanner:
    """Testes para o Planner."""

    @pytest.mark.asyncio
    async def test_plan_com_regras(self):
        planner = Planner()
        steps = await planner.plan("Criar um sistema ERP completo")

        assert len(steps) > 0
        assert all(isinstance(s, Step) for s in steps)
        assert all(s.status == "pending" for s in steps)

    @pytest.mark.asyncio
    async def test_plan_com_llm(self):
        mock_response = json.dumps([
            {
                "description": "Analisar requisitos",
                "depends_on": [],
                "assigned_agent": "planner_agent",
                "expected_output": "Documento de requisitos",
                "priority": 1,
                "estimated_complexity": "high",
            },
            {
                "description": "Projetar arquitetura",
                "depends_on": [0],
                "assigned_agent": "architect_agent",
                "expected_output": "Diagrama de arquitetura",
                "priority": 1,
                "estimated_complexity": "high",
            },
        ])

        llm = MockLLMProvider(response=mock_response)
        planner = Planner(llm_provider=llm)

        steps = await planner.plan("Criar um sistema ERP")

        assert len(steps) == 2
        assert steps[0].description == "Analisar requisitos"
        assert steps[1].description == "Projetar arquitetura"
        assert len(llm.calls) == 1

    @pytest.mark.asyncio
    async def test_plan_fallback_para_regras(self):
        llm = MockLLMProvider(response="resposta inválida")
        planner = Planner(llm_provider=llm)

        steps = await planner.plan("Criar um projeto")

        # Should fall back to rule-based decomposition
        assert len(steps) > 0

    @pytest.mark.asyncio
    async def test_get_ready_steps(self):
        planner = Planner()
        steps = await planner.plan("Projeto\nTeste\nDeploy")

        ready = planner.get_ready_steps()
        assert len(ready) > 0

    @pytest.mark.asyncio
    async def test_mark_completed(self):
        planner = Planner()
        steps = await planner.plan("Projeto\nTeste")

        planner.mark_completed(steps[0].id)
        assert steps[0].status == "completed"

    @pytest.mark.asyncio
    async def test_mark_failed(self):
        planner = Planner()
        steps = await planner.plan("Projeto\nTeste")

        planner.mark_failed(steps[0].id)
        assert steps[0].status == "failed"

    @pytest.mark.asyncio
    async def test_clear(self):
        planner = Planner()
        await planner.plan("Projeto")
        assert len(planner.get_steps()) > 0

        planner.clear()
        assert len(planner.get_steps()) == 0

    @pytest.mark.asyncio
    async def test_decomposicao_fases(self):
        planner = Planner()
        steps = await planner.plan("Sistema completo")

        # Should have planning, implementation, quality, delivery phases
        descriptions = [s.description.lower() for s in steps]
        assert any("analisar" in d or "arquitetura" in d for d in descriptions)
        assert any("implementar" in d or "backend" in d for d in descriptions)
        assert any("test" in d for d in descriptions)
        assert any("document" in d or "deploy" in d for d in descriptions)
