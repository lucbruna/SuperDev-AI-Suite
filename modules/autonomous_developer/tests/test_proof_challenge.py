"""Desafio de prova — ciclo completo do Autonomous Developer (P0-2).

Prova, sem rede e de forma determinística, que o loop inteiro funciona de
ponta a ponta:  plan -> implement -> test -> review  com provider LLM
mockado. Exige três artefatos:  testes passando, diff aplicado e artefato
de PR.

Como o desafio é construído:

1. Um repo sintético com um bug real (``calc.add`` subtrai em vez de somar)
   e testes que FALHAM antes do loop — prova que o bug é real.
2. Um "planner cujo cérebro é um LLM mockado": o LLMClient determinístico
   devolve um plano JSON (o que um LLM real devolveria) e o planner real o
   converte em TaskPlan com FileChange.
3. O CodeGenerator real aplica as mudanças no repo (com regras de
   segurança, backups e escrita atômica).
4. Um validator que roda os TESTES REAIS do repo via pytest.
5. O CodeReviewer real revisa e aprova as mudanças.
6. A fase MERGE do runtime (GitPrExecutor) fecha o loop: branch de trabalho,
   commit, diff main..branch e artefato de PR.

Também prova que os portões funcionam:  o validator bloqueia um "fix"
errado (estado error, testes falhos) e o reviewer rejeita conteúdo
secret-like.

Rode com:  python -m pytest modules/autonomous_developer/tests/test_proof_challenge.py -q
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from pathlib import Path

import pytest

from modules.autonomous_developer.config.constants import (
    PHASE_IMPLEMENT,
    PHASE_MERGE,
    PHASE_PLAN,
    PHASE_REVIEW,
    PHASE_TEST,
)
from modules.autonomous_developer.config.developer_config import DeveloperConfig
from modules.autonomous_developer.core.models import FileChange, ReviewVerdict, TaskPlan
from modules.autonomous_developer.core.registry import DeveloperRegistry
from modules.autonomous_developer.core.runtime import DeveloperRuntime
from modules.autonomous_developer.execution.merge import GitPrExecutor
from modules.autonomous_developer.generator.generator import CodeGenerator, GenerationResult
from modules.autonomous_developer.llm.client import LLMClient
from modules.autonomous_developer.planner.project_planner import ProjectPlanner
from modules.autonomous_developer.review.reviewer import (
    VERDICT_APPROVED,
    VERDICT_REJECTED,
    CodeReviewer,
)
from modules.autonomous_developer.validation.test_runner import TestRunnerValidator

PHASES = (PHASE_PLAN, PHASE_IMPLEMENT, PHASE_TEST, PHASE_REVIEW, PHASE_MERGE)

BUGGY_CALC = '''"""Simple calculator module."""


def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a - b  # bug: subtracts instead of adding
'''

FIXED_CALC = '''"""Simple calculator module."""


def add(a: int, b: int) -> int:
    """Return the sum of a and b."""
    return a + b
'''

TEST_CALC = '''"""Tests for the calc module."""
from calc import add


def test_add_positive():
    assert add(1, 2) == 3


def test_add_negative():
    assert add(-1, 1) == 0


def test_add_zero():
    assert add(0, 0) == 0
'''

# Resposta "do LLM": um plano JSON. Um LLM real devolveria o mesmo formato.
MOCK_PLAN_JSON = json.dumps(
    {
        "goal": "Fix add() so it returns the sum of its operands",
        "tasks": [
            {
                "title": "Fix add() implementation",
                "description": "add() currently subtracts; it must return the sum.",
                "priority": "high",
                "risk": "low",
                "files": [
                    {
                        "path": "calc.py",
                        "operation": "modify",
                        "old_content": "    return a - b\n",
                        "content": FIXED_CALC,
                        "reason": "Fix wrong operator: a - b should be a + b",
                    }
                ],
            }
        ],
    }
)


def _count(pattern: str, text: str) -> int:
    match = re.search(pattern, text)
    return int(match.group(1)) if match else 0


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [
            "git",
            "-c",
            "user.name=autonomous_developer",
            "-c",
            "user.email=dev@super.local",
            *args,
        ],
        cwd=repo,
        capture_output=True,
        text=True,
        check=True,
    )


def _run_pytest(repo: Path) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        [sys.executable, "-m", "pytest", "-q", "--no-header", "-p", "no:cacheprovider"],
        cwd=repo,
        capture_output=True,
        text=True,
        timeout=180,
    )


class MockLLMPlanner:
    """Planner cujo 'cérebro' é um LLM mockado (LLMClient determinístico).

    Simula a arquitetura real:  o LLM recebe goal + estado atual do repo e
    devolve um plano JSON; o ProjectPlanner converte o JSON em TaskPlan.
    """

    def __init__(self, llm: LLMClient | None = None) -> None:
        self.llm = llm or LLMClient()
        self._planner = ProjectPlanner()

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        calc_file = Path(ctx.config.project_root) / "calc.py"
        current = calc_file.read_text(encoding="utf-8") if calc_file.exists() else "<missing>"
        prompt = (
            f"Goal: {goal}\n"
            f"Project root: {ctx.config.project_root}\n"
            f"Current calc.py:\n```\n{current}\n```\n"
            "Return a JSON plan with tasks[].files[].path/operation/content."
        )
        response = self.llm.complete(prompt)
        payload = json.loads(response.text)
        plan = self._planner.plan(payload["goal"], tasks=payload["tasks"])
        ctx.record("task_count", len(plan.tasks))
        ctx.record("llm_provider", response.provider)
        ctx.publish("plan.ready", {"goal": plan.goal, "task_count": len(plan.tasks)})
        return plan


class RepoTestValidator:
    """Roda os TESTES REAIS do repo (pytest) e falha a fase se não passarem.

    Delegates to the module's real sandboxed test-runner validator so the
    proof exercises the production component (no shell, env sanitized).
    """

    def __init__(self, timeout: int = 180) -> None:
        self._inner = TestRunnerValidator(timeout_seconds=timeout)

    def run(self, ctx, goal: str, session_id: str | None = None, **kwargs):
        return self._inner.run(ctx, goal, session_id=session_id, **kwargs)


def _build_runtime(repo: Path, plan_json: str) -> DeveloperRuntime:
    registry = DeveloperRegistry()
    registry.register(
        "planner", "default", MockLLMPlanner(LLMClient(mock_response=plan_json))
    )
    registry.register("generator", "default", CodeGenerator())
    registry.register("validator", "default", RepoTestValidator())
    registry.register("reviewer", "default", CodeReviewer())
    registry.register("executor", "default", GitPrExecutor())
    config = DeveloperConfig(
        project_root=str(repo),
        mode="supervised",
        work_branch="fix/calc-add",
        run_tests=True,
        run_review=True,
        create_pr=True,
    )
    return DeveloperRuntime(config=config, registry=registry)


@pytest.fixture()
def challenge_repo(tmp_path: Path):
    """Repo sintético com bug real, versionado em git (branch main)."""
    repo = tmp_path / "repo"
    repo.mkdir()
    (repo / "calc.py").write_text(BUGGY_CALC, encoding="utf-8")
    (repo / "test_calc.py").write_text(TEST_CALC, encoding="utf-8")
    _git(repo, "init", "-b", "main")
    _git(repo, "add", "calc.py", "test_calc.py")
    _git(repo, "commit", "-m", "initial: add() has a bug (subtracts)")
    # Prova do bug: os testes falham ANTES do loop.
    before = _run_pytest(repo)
    assert before.returncode != 0, "pre-loop pytest should fail on the buggy repo"
    return repo, tmp_path


def test_proof_challenge_loop_end_to_end(challenge_repo):
    """O loop completo entrega: testes passando, diff aplicado e PR."""
    repo, _ = challenge_repo
    runtime = _build_runtime(repo, MOCK_PLAN_JSON)
    ctx = runtime.execute(
        "Fix add() so it returns the sum of its operands", phases=PHASES
    )

    # 1. Loop concluído com sucesso (state ready + sessão completed).
    state = ctx.state.to_dict()
    assert state["state"] == "ready", state
    sessions = ctx.sessions.recent()
    assert sessions and sessions[0].status == "completed", ctx.sessions.recent()
    session_id = sessions[0].session_id

    # 2. Artefatos de cada fase do loop.
    plan = ctx.get_artifact(PHASE_PLAN)
    assert isinstance(plan, TaskPlan) and plan.tasks, "plan artifact missing/empty"
    impl = ctx.get_artifact(PHASE_IMPLEMENT)
    assert isinstance(impl, GenerationResult) and impl.success, impl.to_dict()
    assert "calc.py" in impl.written, impl.written
    test_result = ctx.get_artifact(PHASE_TEST)
    assert test_result["passed"] >= 3 and test_result["failed"] == 0, test_result
    review = ctx.get_artifact(PHASE_REVIEW)
    assert isinstance(review, ReviewVerdict) and review.verdict == VERDICT_APPROVED, review

    # 3. Código corrigido em disco E os testes reais passam após o loop.
    fixed = (repo / "calc.py").read_text(encoding="utf-8")
    assert "return a + b" in fixed
    assert "return a - b" not in fixed
    after = _run_pytest(repo)
    assert after.returncode == 0, (after.stdout + after.stderr)[-3000:]

    # 4. A fase MERGE do próprio runtime fechou o loop: branch de trabalho,
    # commit, diff aplicado e artefato de PR.
    merge = ctx.get_artifact(PHASE_MERGE)
    assert merge is not None, "merge phase did not produce an artifact"
    assert merge.base_branch == "main", merge.to_dict()
    assert merge.branch == "fix/calc-add", merge.to_dict()
    assert merge.commit, "merge phase must commit the change"
    assert "calc.py" in merge.files, merge.to_dict()
    assert "+    return a + b" in merge.diff, "diff does not contain the fix"
    branches = _git(repo, "branch", "--list", "fix/calc-add").stdout
    assert "fix/calc-add" in branches

    # Artefato de PR escrito pelo executor sob o data_dir do runtime.
    assert merge.pr_artifact, merge.to_dict()
    pr_artifact = Path(merge.pr_artifact)
    assert pr_artifact.exists()
    pr_body = pr_artifact.read_text(encoding="utf-8")
    assert "Fix add()" in pr_body
    assert session_id in pr_body
    assert "```diff" in pr_body


def test_validator_blocks_bad_fix(challenge_repo):
    """Um 'fix' errado (LLM não corrige o bug) é bloqueado pela fase de teste."""
    repo, _ = challenge_repo
    wrong_plan = json.loads(MOCK_PLAN_JSON)
    wrong_plan["tasks"][0]["files"][0]["content"] = BUGGY_CALC
    runtime = _build_runtime(repo, json.dumps(wrong_plan))
    ctx = runtime.execute(
        "Fix add() so it returns the sum of its operands", phases=PHASES
    )

    state = ctx.state.to_dict()
    assert state["state"] == "error", state
    assert ctx.stats.get("tests_failed", 0) >= 1, ctx.stats
    sessions = ctx.sessions.recent()
    assert sessions and sessions[0].status == "failed", ctx.sessions.recent()
    # A fase de review nem chegou a rodar — o portão de testes bloqueou.
    assert ctx.get_artifact(PHASE_REVIEW) is None


def test_reviewer_rejects_secret_like_content():
    """O reviewer rejeita conteúdo secret-like (portão de segurança real)."""
    reviewer = CodeReviewer()
    verdict = reviewer.review_changes(
        [FileChange(path="calc.py", content="api_key = 'sk-123456789'")],
        project_root=".",
    )
    assert verdict.verdict == VERDICT_REJECTED
    assert any("Secret" in issue for issue in verdict.issues)
