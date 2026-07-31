"""Tests for the executable ``examples/devops-subsystems`` example (full delivery flow).

Valida a saída do fluxo completo do exemplo: docker build -> pipeline CICD ->
provision multi-subsistema -> deploy com quality gate -> rollback + histórico ->
persistência JSON -> destroy.

O diretório do exemplo contém hífen ('devops-subsystems'), logo não é um pacote
Python importável — carregamos o ``main.py`` por caminho via ``importlib``.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

_EXAMPLE_MAIN = Path(__file__).resolve().parents[2] / "examples" / "devops-subsystems" / "main.py"
_spec = importlib.util.spec_from_file_location("devops_subsystems_example_main", _EXAMPLE_MAIN)
if _spec is None or _spec.loader is None:  # pragma: no cover - file always exists
    raise ImportError(f"could not load example: {_EXAMPLE_MAIN}")
_example = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(_example)
run_demo = _example.run_demo
main = _example.main

_EXPECTED_PERSISTED_FILES = {
    "builds.json",
    "cicd.json",
    "deployments.json",
    "docker.json",
    "environments.json",
    "environments_lifecycle.json",
    "history.json",
    "strategy_state.json",
    "terraform.json",
}


class TestDevOpsSubsystemsExample:
    def test_full_flow_output(self, tmp_path: Path) -> None:
        result = run_demo(tmp_path / "devops-store")

        assert result["image"] == "billing-api:v1.4.0"
        assert result["pipeline_status"] == "passed"
        assert result["provisioned"] == "provisioned"
        assert result["blocked_gate"] == "blocked"
        assert result["deploy"] == "canary"
        assert result["deployment_id"].startswith("dep-")
        assert result["rollback"] == "rolled_back"
        assert result["history_count"] >= 2  # deploy + rollback
        assert result["destroyed"] == "destroyed"
        assert set(result["persisted_files"]) == _EXPECTED_PERSISTED_FILES

    def test_main_entrypoint_runs(self) -> None:
        result = main()
        assert result["pipeline_status"] == "passed"
        assert result["deploy"] == "canary"
        assert result["rollback"] == "rolled_back"
        assert result["destroyed"] == "destroyed"
        assert result["deployment_id"].startswith("dep-")
