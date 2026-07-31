"""SuperDev DevOps — Subsistemas integrados: exemplo prático.

Demonstra o fluxo completo de entrega usando o ``DevOpsEngine`` com os
subsistemas reais (docker / cloud / environments / terraform / cicd) +
production gate do QualityEngine + persistência JSON em disco:

    1. docker build ......... imagem criada no DockerEngine
    2. pipeline CICD ........ build -> test -> security -> artifact (passed)
    3. provision ............ cloud + environments + terraform (multi-subsistema)
    4. deploy quality gate . BLOQUEADO (sinais fracos) -> APROVADO (canary real)
    5. rollback + histórico . rollback do deploy + audit trail
    6. persistência ......... save_state() + reload num engine novo
    7. destroy .............. limpa o ambiente provisionado

Execute com:
    python examples/devops-subsystems/main.py
"""

from __future__ import annotations

import shutil
import sys
import tempfile
from pathlib import Path

# Ensure the SuperDev repo root is importable when run as a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from devops.devops_engine import DevOpsEngine  # noqa: E402


def run_demo(store_path: Path) -> dict:
    engine = DevOpsEngine(store_path=store_path)

    print("=== 1) DOCKER BUILD — imagem a partir do contexto ===")
    built = engine.build("billing-api", version="v1.4.0", path="./services/billing")
    print(f"build {built['build_id']} -> imagem {built['image']} ({built['status']})")
    images = [i.get("tag") or i.get("image") for i in engine.docker.list_images()]
    print(f"imagens no DockerEngine: {engine.docker.status()['images']} -> {images}")

    print("\n=== 2) PIPELINE CICD — release (build/test/security/artifact) ===")
    engine.cicd.builder.create(
        "release",
        stages=[
            {"name": "build", "type": "build", "config": {"project": "billing-api"}},
            {"name": "test", "type": "test", "config": {"total": 24, "failed": 0}},
            {"name": "security", "type": "security", "config": {"project": "billing-api"}},
            {"name": "artifact", "type": "artifact",
             "config": {"name": "billing-api", "version": "v1.4.0"}},
        ],
    )
    run = engine.cicd.run_pipeline("release")
    stages = ", ".join(f"{s['type']}:{s['status']}" for s in run["stages"])
    print(f"pipeline 'release' -> {run['status']} | stages: [{stages}]")
    print(f"pipelines: {engine.cicd.status()['pipelines']} | runs: {engine.cicd.status()['runs']}")

    print("\n=== 3) PROVISION — cloud + environments + terraform ===")
    tf_plan = engine.terraform.plan("./infra/billing", names=["db", "cache"])
    engine.terraform.apply("./infra/billing", resources=tf_plan["resources"])
    print(f"terraform: {len(tf_plan['resources'])} recursos aplicados -> "
          f"state_list={engine.terraform.state_list('./infra/billing')}")
    cost = engine.cloud.estimate_cost("local", {"resource_type": "compute", "instances": 2})
    print(f"cloud: custo estimado ${cost['monthly_estimate']:.2f}/mês "
          f"(providers registrados: {sorted(engine.cloud.providers.list())})")
    prov = engine.provision("staging", resource_types=["compute", "database", "network"])
    print(f"environments: '{prov['environment']}' criado ({prov['status']}) com "
          f"{len(prov['resources'])} recursos no engine e "
          f"{len(prov['cloud_resources'])} no CloudEngine")
    engine.environments.set_variable("staging", "API_KEY", "sk-demo-123")
    print(f"variável de ambiente: API_KEY={engine.environments.variables('staging')['API_KEY']}")

    print("\n=== 4) DEPLOY COM QUALITY GATE ===")
    blocked = engine.deploy_with_quality(
        "billing-api",
        "production",
        version="v1.4.0",
        signals={
            "quality_score": 0.58,
            "coverage": 0.35,
            "tests_passed": False,
            "critical_findings": 2,
        },
    )
    print(f"deploy (sinais fracos) -> {blocked['status']} "
          f"(deployed={blocked['deployed']}) | gate: {blocked['gate']['decision']}")
    for reason in blocked["gate"]["blocked_reasons"]:
        print(f"  [x] {reason}")
    approved = engine.deploy_with_quality(
        "billing-api",
        "production",
        version="v1.4.0",
        strategy="canary",
        signals={
            "quality_score": 0.94,
            "coverage": 0.92,
            "tests_passed": True,
            "critical_findings": 0,
        },
    )
    print(f"deploy (sinais bons) -> {approved['status']} "
          f"(deployed={approved['deployed']}) | gate: {approved['gate']['decision']}")
    dep_id = approved["deployment_id"]
    for _ in range(4):
        state = engine.deployment.advance(dep_id)
        print(f"  canary -> traffic {state['strategy_status']['traffic']:.0%}")
        if state["status"] == "healthy":
            break
    print(f"deploy {dep_id}: {engine.deployment.status(dep_id)['status']}")

    print("\n=== 5) ROLLBACK + HISTÓRICO ===")
    rolled = engine.deployment.rollback(dep_id)
    print(f"rollback {dep_id} -> {rolled['status']}")
    history = engine.deployment.history("billing-api")
    for entry in history:
        print(f"  {entry['deployment_id']} {entry['service']}:{entry['version']} "
              f"({entry['strategy']}) -> {entry['status']}")
    print(f"audit trail: {len(history)} entrada(s) para billing-api")

    print("\n=== 6) PERSISTÊNCIA — save_state() + reload ===")
    metrics = engine.metrics.snapshot().get("counters", {})
    engine.save_state()
    files = sorted(p.name for p in store_path.glob("*.json"))
    print(f"arquivos persistidos: {files}")
    reloaded = DevOpsEngine(store_path=store_path)
    print(f"reload: builds={reloaded.status()['build_count']} | "
          f"imagens={reloaded.docker.status()['images']} | "
          f"pipelines={reloaded.cicd.status()['pipelines']} | "
          f"runs={reloaded.cicd.status()['runs']} | "
          f"environments={reloaded.status()['environment_count']}")
    print(f"API_KEY após reload: {reloaded.environments.variables('staging')['API_KEY']}")
    print(f"deploy {dep_id} após reload: "
          f"{reloaded.deployment.status(dep_id)['status']}")

    print("\n=== 7) DESTROY — limpeza do ambiente ===")
    destroyed = reloaded.destroy("staging")
    print(f"destroy staging -> {destroyed['status']} "
          f"(recursos removidos: {len(destroyed['resources'])})")
    print(f"status final: environments={reloaded.status()['environment_count']} | "
          f"terraform: staging={reloaded.terraform.state_list('./terraform/staging')} | "
          f"infra/billing={reloaded.terraform.state_list('./infra/billing')}")

    print("\n=== MÉTRICAS DO DEVOPS ===")
    print(f"builds: {metrics.get('devops.builds', 0)} | "
          f"provisions: {metrics.get('devops.provisions', 0)} | "
          f"deploys: {metrics.get('devops.deploys', 0)} | "
          f"blocked: {metrics.get('devops.deploys_blocked', 0)} | "
          f"rollbacks: {metrics.get('devops.rollbacks', 0)}")
    # O destroy roda no engine recarregado — lemos as métricas dele aqui.
    reloaded_metrics = reloaded.metrics.snapshot().get("counters", {})
    print(f"destroys (engine recarregado): {reloaded_metrics.get('devops.destroys', 0)}")

    return {
        "image": built["image"],
        "pipeline_status": run["status"],
        "provisioned": prov["status"],
        "blocked_gate": blocked["gate"]["decision"],
        "deploy": approved["status"],
        "deployment_id": dep_id,
        "rollback": rolled["status"],
        "history_count": len(history),
        "persisted_files": files,
        "destroyed": destroyed["status"],
    }


def main() -> dict:
    store_path = Path(tempfile.mkdtemp(prefix="superdev-devops-state-"))
    try:
        return run_demo(store_path)
    finally:
        shutil.rmtree(store_path, ignore_errors=True)


if __name__ == "__main__":
    result = main()
    print(f"\nResultado: {result}")
