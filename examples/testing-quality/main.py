"""Volume 15 — Testing & Quality Engine: exemplo prático.

Demonstra o ciclo completo de qualidade:
    código -> testes unitários -> integração -> performance -> cobertura ->
    análise de qualidade -> verificação de segurança -> quality score ->
    production gate -> link ao fluxo de deploy via DevOpsQualityGate.

O quality score calculado alimenta o DevOpsQualityGate (devops) — quando o
gate aprova, um deploy REAL é executado pelo DeploymentEngine.

Execute com:
    python examples/testing-quality/main.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure the SuperDev repo root is importable when run as a script
# (`python examples/testing-quality/main.py` adds only this file's dir to sys.path).
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from devops.deployment.quality_gate import DevOpsQualityGate  # noqa: E402
from devops.devops_engine import DevOpsEngine  # noqa: E402
from quality.quality_engine import QualityEngine  # noqa: E402

OUTPUT_DIR = Path(__file__).parent / "output"


async def main() -> None:
    engine = QualityEngine()
    await engine.start()

    # 1) Testes unitários gerados a partir do código-fonte do "módulo".
    source = "def calcular_total(itens, desconto=0.0):\n    return sum(itens) * (1 - desconto)\n"
    suite = engine.unit.generate_suite("billing_core", source=source)
    unit_result = await engine.testing.run_suite(suite)
    print(f"[unit] {unit_result.status.value} — {unit_result.passed}/{unit_result.total} passaram")

    # 2) Suíte de integração entre módulos (API + workflow).
    it_suite = engine.integration.create_suite(name="checkout_flow", category="api")
    engine.integration.add_api_test(it_suite.suite_id, "/api/v1/checkout", expected_status=200)
    engine.integration.add_workflow_test(it_suite.suite_id, "cart->checkout", expected_steps=2)
    integration_result = await engine.testing.run_suite(it_suite)
    print(f"[integration] {integration_result.status.value} — "
          f"{integration_result.passed}/{integration_result.total} passaram")

    # 3) Performance: latência e throughput de uma operação simulada.
    latency = engine.performance.latency(lambda: 0.005, samples=50)
    rate = engine.performance.throughput(lambda: None, duration_s=0.5)
    print(f"[performance] latência média {latency['avg_ms']:.2f} ms | "
          f"throughput {rate:.0f} ops/s")

    # 4) Cobertura simulada de um módulo.
    coverage = engine.coverage.measure(
        "billing.py", {"covered_lines": 10, "total_lines": 11}
    )
    print(f"[coverage] line {coverage.line:.0%} | score {coverage.overall:.1%}")

    # 5) Análise de qualidade do código.
    analysis = engine.analysis.analyze_code("billing_core", source)
    print(f"[analysis] quality={analysis['quality']:.2f} "
          f"maintainability={analysis['maintainability']:.2f}")

    # 6) Verificação de segurança (vulnerabilidades simuladas).
    findings = engine.security.vulnerability_scan(
        "billing-api", "session = request.cookies['token']"
    )
    dep = engine.security.scan_dependency("requests", "2.31.0")
    print(f"[security] {len(findings)} finding(s) em código | "
          f"dependência requests: risco {dep['risk']}")

    # 7) Relatório de testes consolidado + export.
    report_id = await engine.reports.create_test_report("billing", unit_result)
    print(f"[reports] relatório gerado: {report_id[:8]}…")

    # 8) Quality score + Production Gate.
    score = engine.compute_score(
        "billing",
        code=analysis["quality"],
        tests=unit_result.passed_rate,
        security=0.98,
        performance=0.90,
        documentation=0.88,
    )
    print(f"[quality] score={score['overall']:.1%} "
          f"(code={score['code']:.0%} tests={score['tests']:.0%} "
          f"security={score['security']:.0%} performance={score['performance']:.0%} "
          f"docs={score['documentation']:.0%})")

    gate = await engine.evaluate_production_gate(
        "billing",
        {
            "quality_score": score["overall"],
            "coverage": coverage.overall,
            "tests_passed": unit_result.passed_rate,
            "security_clean": len(findings) == 0,
        },
    )
    print(f"[gate] production gate: {gate['decision']} "
          f"({'aprovado' if gate['decision'] == 'approved' else 'bloqueado'})")

    # 9) Link do quality score ao fluxo de deploy (DevOpsQualityGate).
    deploy_signals = {
        "quality_score": score["overall"],
        "coverage": coverage.overall,
        "tests_passed": unit_result.passed_rate,
        "security_clean": len(findings) == 0,
    }
    deploy_gate = DevOpsQualityGate()
    deploy_check = await deploy_gate.evaluate("billing", deploy_signals)
    print(f"[deploy-gate] DevOpsQualityGate: {deploy_check['decision']} "
          f"(quality_score={deploy_check.get('quality_score', 0.0):.1%})")

    devops = DevOpsEngine()
    deployment_id = None
    if deploy_check["decision"] == "approved":
        # Gate aprovou -> deploy REAL via DeploymentEngine (estratégia canary).
        deployment = devops.deployment.deploy(
            "billing", "v1.4.2", strategy="canary", environment="production"
        )
        deployment_id = deployment["deployment_id"]
        print(f"[deploy] APROVADO -> deploy real: {deployment_id} "
              f"({deployment['status']})")
        # Avança o canary até 100% do tráfego.
        for _ in range(6):
            state = devops.deployment.advance(deployment_id)
            if state["status"] == "healthy":
                break
        print(f"[deploy] canary promovido -> {devops.deployment.status(deployment_id)['status']}")
    else:
        print("[deploy] BLOQUEADO -> nenhum deploy executado")
        for reason in deploy_check.get("blocked_reasons", []):
            print(f"  [x] {reason}")

    OUTPUT_DIR.mkdir(exist_ok=True)
    markdown_path = OUTPUT_DIR / "quality_report.md"
    engine.reports.export_markdown(report_id, str(markdown_path))
    print(f"[export] relatório salvo em {markdown_path}")

    await engine.stop()

    return {
        "unit": unit_result.status.value,
        "integration": integration_result.status.value,
        "latency_ms": latency["avg_ms"],
        "throughput": rate,
        "coverage": coverage.overall,
        "analysis_quality": analysis["quality"],
        "security_findings": len(findings),
        "quality_score": score["overall"],
        "gate": gate["decision"],
        "deploy_gate": deploy_check["decision"],
        "deployment_id": deployment_id,
    }


if __name__ == "__main__":
    asyncio.run(main())
