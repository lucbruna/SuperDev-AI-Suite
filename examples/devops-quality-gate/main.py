"""Volume 15+ — Quality Gate + DeploymentEngine real: exemplo prático.

Demonstra o production gate do QualityEngine bloqueando deploys abaixo do
padrão de qualidade e, quando aprovado, executando um deploy REAL via o
DeploymentEngine (estratégias rolling / canary / blue-green):

    1. Deploy com sinais fracos  -> BLOQUEADO (nenhum deploy executado)
    2. Deploy com sinais bons    -> APROVADO (deploy real executado)
    3. Status, avanço canary e rollback do deploy executado

Execute com:
    python examples/devops-quality-gate/main.py
"""

from __future__ import annotations

import sys
from pathlib import Path

# Ensure the SuperDev repo root is importable when run as a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from devops.devops_engine import DevOpsEngine  # noqa: E402


def main() -> None:
    engine = DevOpsEngine()

    print("=== Deploy 1: sinais fracos (deve ser BLOQUEADO) ===")
    first = engine.deploy_with_quality(
        "billing-api",
        "production",
        signals={
            "quality_score": 0.62,
            "coverage": 0.40,
            "tests_passed": False,
            "critical_findings": 1,
        },
    )
    print(f"status: {first['status']} | deployed: {first['deployed']}")
    for reason in first["gate"]["blocked_reasons"]:
        print(f"  [x] {reason}")

    print("\n=== Deploy 2: sinais bons (deve ser APROVADO + deploy REAL) ===")
    second = engine.deploy_with_quality(
        "billing-api",
        "production",
        version="v2.3.0",
        strategy="canary",
        signals={
            "quality_score": 0.93,
            "coverage": 0.91,
            "tests_passed": True,
            "critical_findings": 0,
        },
    )
    print(f"status: {second['status']} | deployed: {second['deployed']}")
    print(f"quality_score: {second['gate']['quality_score']:.2f}")
    dep_id = second["deployment_id"]
    print(f"deployment_id: {dep_id} | strategy: {second['deployment']['strategy']}")

    print("\n=== Avançando o canary até 100% do tráfego ===")
    for _ in range(4):
        state = engine.deployment.advance(dep_id)
        print(f"  canary step -> traffic {state['strategy_status']['traffic']:.0%}")
        if state["status"] == "healthy":
            break

    print("\n=== Status do deployment executado ===")
    status = engine.deployment.status(dep_id)
    print(f"status: {status['status']} | service: {status['service']} | version: {status['version']}")

    print("\n=== Rollback do deployment ===")
    rolled = engine.deployment.rollback(dep_id)
    print(f"status: {rolled['status']}")

    print("\n=== Histórico de deployments ===")
    for entry in engine.deployment.history():
        print(f"  {entry['deployment_id']} {entry['service']} -> {entry['status']}")

    print("\n=== Métricas do DevOps ===")
    metrics = engine.metrics.snapshot()
    print(f"deploys: {metrics.get('counters', {}).get('devops.deploys', 0)}")
    print(f"deploys bloqueados: "
          f"{metrics.get('counters', {}).get('devops.deploys_blocked', 0)}")
    print(f"rollbacks: {metrics.get('counters', {}).get('devops.rollbacks', 0)}")

    return {"first": first, "second": second}


if __name__ == "__main__":
    main()
