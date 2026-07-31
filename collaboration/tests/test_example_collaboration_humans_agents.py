"""Tests for the executable ``examples/collaboration-humans-agents`` example.

Valida o fluxo completo humano + IA do Volume 26: workspace NEXUS ERP PROJECT,
projeto "Sistema Supermercado ERP" (12 humanos + 8 agentes, 74%), solicitação
"Criar aplicativo de vendas" com Planner -> Task Manager -> Coder -> review
humano -> Security -> Testing -> Deploy, e aprovação director
(Developer -> Tech Lead -> Security -> Diretor).

O diretório do exemplo contém hífen ('collaboration-humans-agents'), logo não é
um pacote Python importável — carregamos o ``main.py`` por caminho via
``importlib``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_EXAMPLE_MAIN = (Path(__file__).resolve().parents[2] /
                 "examples" / "collaboration-humans-agents" / "main.py")
_spec = importlib.util.spec_from_file_location(
    "collaboration_humans_agents_example_main", _EXAMPLE_MAIN)
if _spec is None or _spec.loader is None:  # pragma: no cover - file always exists
    raise ImportError(f"could not load example: {_EXAMPLE_MAIN}")
_example = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_example)
run_demo = _example.run_demo
main = _example.main


class TestCollaborationHumansAgentsExample:
    def test_full_flow_output(self) -> None:
        result = run_demo()

        assert result["workspace"] == "NEXUS ERP PROJECT"
        assert result["project"] == "Sistema Supermercado ERP"
        assert result["project_status"] == "active"
        assert result["progress"] >= 74.0
        assert result["members_humans"] == 12
        assert result["members_agents"] == 8
        assert result["teams"] >= 3
        assert result["channels"] >= 3

        assert result["task"] == "Criar aplicativo de vendas"
        assert result["task_status"] == "done"
        assert result["code_review_score"] >= 90.0
        assert result["security_review"] == "changes_requested"
        assert result["testing_review"] == "approved"

        assert result["approval"] == "approved"
        assert result["approval_steps"] == 4  # Developer, Tech Lead, Security, Diretor
        assert result["knowledge_version"] == 2  # create + edit
        assert result["messages"] >= 3
        assert result["metrics"]["counters"]["collab.members"] >= 20  # 12 + 8
        assert result["metrics"]["counters"]["collab.tasks"] >= 1

    def test_main_entrypoint_runs(self) -> None:
        result = main()
        assert result["approval"] == "approved"
        assert result["task_status"] == "done"
        assert result["members_agents"] == 8
