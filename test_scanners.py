"""Script de teste — executa todos os scanners contra diretórios específicos do SuperDev."""

import asyncio
import sys
import os
import signal
from datetime import datetime
from pathlib import Path

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def run_with_timeout(coro, timeout=30):
    """Run a coroutine with a timeout."""
    try:
        return await asyncio.wait_for(coro, timeout=timeout)
    except asyncio.TimeoutError:
        return {"error": f"TIMEOUT after {timeout}s", "findings": 0, "duration_ms": 0, "by_severity": {}}


async def test_scanner(name, scanner_instance, target, timeout=30):
    print(f"\n{'='*50}")
    print(f"[SCAN] {name}")
    print(f"  Target: {target}")
    print(f"{'='*50}")
    try:
        result = await run_with_timeout(scanner_instance.scan(target), timeout)
        if isinstance(result, dict) and result.get("error") == f"TIMEOUT after {timeout}s":
            print(f"  [TIMEOUT] Excedeu {timeout}s")
            return {"name": name, "findings": 0, "duration_ms": 0, "by_severity": {}, "error": result["error"]}

        sev = result.by_severity if hasattr(result, 'by_severity') else {}
        print(f"  Findings: {result.total_findings} | Duracao: {result.scan_duration_ms:.0f}ms")
        print(f"  Severidade: {sev}")
        if result.error:
            print(f"  [WARN] Erro: {result.error}")

        if result.findings:
            print(f"  --- Top findings ---")
            for f in result.findings[:5]:
                file_rel = os.path.relpath(f.file_path) if f.file_path else ""
                line_str = f":{f.line}" if f.line else ""
                cve_str = f" | CVE:{f.cve}" if f.cve else ""
                print(f"  [{f.severity.value.upper():7}] {f.rule_id}: {f.title}{cve_str}")
                print(f"         {file_rel}{line_str}")
        return {"name": name, "findings": result.total_findings, "duration_ms": result.scan_duration_ms, "by_severity": sev, "error": result.error}
    except Exception as e:
        print(f"  [ERROR] {e}")
        return {"name": name, "error": str(e)[:100], "findings": 0, "duration_ms": 0, "by_severity": {}}


async def test_security(name, analyzer_instance, target, timeout=30):
    print(f"\n{'='*50}")
    print(f"[SEC]  {name}")
    print(f"  Target: {target}")
    print(f"{'='*50}")
    try:
        result = await run_with_timeout(analyzer_instance.analyze(target), timeout)
        if isinstance(result, dict) and result.get("error") == f"TIMEOUT after {timeout}s":
            print(f"  [TIMEOUT] Excedeu {timeout}s")
            return {"name": name, "findings": 0, "duration_ms": 0, "by_severity": {}, "error": result["error"]}

        sev = result.by_severity if hasattr(result, 'by_severity') else {}
        print(f"  Findings: {result.total_findings} | Duracao: {result.scan_duration_ms:.0f}ms")
        print(f"  Severidade: {sev}")
        if result.error:
            print(f"  [WARN] Erro: {result.error}")

        if result.findings:
            print(f"  --- Top findings ---")
            for f in result.findings[:5]:
                file_rel = os.path.relpath(f.file_path) if f.file_path else ""
                line_str = f":{f.line}" if f.line else ""
                cve_str = f" | CVE:{f.cve}" if f.cve else ""
                print(f"  [{f.severity.value.upper():7}] {f.rule_id}: {f.title}{cve_str}")
                print(f"         {file_rel}{line_str}")

        # SBOM-specific
        if hasattr(result, 'metadata') and result.metadata and 'sbom' in result.metadata:
            sbom = result.metadata['sbom']
            print(f"  [SBOM] {sbom.get('dependencies_count', 0)} components, format: {sbom.get('bomFormat', '?')}")

        return {"name": name, "findings": result.total_findings, "duration_ms": result.scan_duration_ms, "by_severity": sev, "error": result.error}
    except Exception as e:
        print(f"  [ERROR] {e}")
        return {"name": name, "error": str(e)[:100], "findings": 0, "duration_ms": 0, "by_severity": {}}


async def main():
    start = datetime.now()
    root = os.path.dirname(os.path.abspath(__file__))
    backend_dir = os.path.join(root, "backend")
    infra_dir = os.path.join(root, "infrastructure")
    scanners_dir = os.path.join(root, "scanners")
    security_dir = os.path.join(root, "security")
    core_dir = os.path.join(root, "core")

    print(f"{'#'*50}")
    print(f"#  SUPERDEV SCANNERS - TESTE")
    print(f"#  Target dirs: backend/, infrastructure/, scanners/, security/")
    print(f"#  Inicio: {start.isoformat()}")
    print(f"{'#'*50}")

    results = []

    # === SCANNERS ===
    print(f"\n{'='*50}")
    print(f"[SCANNERS]")
    print(f"{'='*50}")

    # 1. Filesystem - scan just scanners/ dir (fast)
    from scanners.filesystem.scanner import FilesystemScanner
    results.append(await test_scanner("FilesystemScanner", FilesystemScanner(), scanners_dir, timeout=15))

    # 2. SourceCode - scan backend/ dir
    from scanners.source_code.scanner import SourceCodeScanner
    results.append(await test_scanner("SourceCodeScanner", SourceCodeScanner(), backend_dir, timeout=30))

    # 3. Dependencies - scan root for requirements.txt / package.json
    from scanners.dependencies.scanner import DependencyScanner
    results.append(await test_scanner("DependencyScanner", DependencyScanner(), root, timeout=10))

    # 4. Docker - scan infrastructure/
    from scanners.docker.scanner import DockerScanner
    results.append(await test_scanner("DockerScanner", DockerScanner(), infra_dir, timeout=10))

    # 5. Kubernetes - scan infrastructure/ for yaml
    from scanners.kubernetes.scanner import KubernetesScanner
    results.append(await test_scanner("KubernetesScanner", KubernetesScanner(), infra_dir, timeout=10))

    # 6. Terraform - scan infrastructure/
    from scanners.terraform.scanner import TerraformScanner
    results.append(await test_scanner("TerraformScanner", TerraformScanner(), infra_dir, timeout=10))

    # 7. Cloud - scan infrastructure/
    from scanners.cloud.scanner import CloudScanner
    results.append(await test_scanner("CloudScanner", CloudScanner(), infra_dir, timeout=10))

    # 8. Secrets - scan backend/ (most code)
    from scanners.secrets.scanner import SecretsScanner
    results.append(await test_scanner("SecretsScanner", SecretsScanner(), backend_dir, timeout=30))

    # === SECURITY ===
    print(f"\n{'='*50}")
    print(f"[SECURITY]")
    print(f"{'='*50}")

    # 9. OWASP - scan backend/
    from security.owasp.analyzer import OWASPAnalyzer
    results.append(await test_security("OWASPAnalyzer", OWASPAnalyzer(), backend_dir, timeout=30))

    # 10. SecretsDetector - scan backend/
    from security.secrets_detector.detector import SecretsDetector
    results.append(await test_security("SecretsDetector", SecretsDetector(), backend_dir, timeout=30))

    # 11. VulnerabilityEngine - scan root (deps files)
    from security.vulnerability_engine.engine import VulnerabilityEngine
    results.append(await test_security("VulnerabilityEngine", VulnerabilityEngine(), root, timeout=10))

    # 12. SecurityDependencyScanner - scan root
    from security.dependency_scan.scanner import SecurityDependencyScanner
    results.append(await test_security("SecurityDependencyScanner", SecurityDependencyScanner(), root, timeout=10))

    # 13. SBOMGenerator - scan root
    from security.sbom.generator import SBOMGenerator
    results.append(await test_security("SBOMGenerator", SBOMGenerator(), root, timeout=15))

    # === SUMMARY ===
    elapsed = (datetime.now() - start).total_seconds()
    total_findings = sum(r.get("findings", 0) for r in results)
    errors = [r for r in results if r.get("error")]

    print(f"\n{'='*50}")
    print(f"[RESUMO]")
    print(f"{'='*50}")
    print(f"  Modulos: {len(results)}")
    print(f"  Findings: {total_findings}")
    print(f"  Tempo: {elapsed:.0f}s")
    if errors:
        print(f"  [ERRO] Modulos com erro: {len(errors)}")
        for e in errors:
            print(f"    {e['name']}: {str(e.get('error',''))[:80]}")
    else:
        print(f"  [OK] Todos executaram sem erros")
    print()
    print(f"  {'MODULO':30s} | {'#':>3s} | {'TEMPO':>7s} | SEVERIDADE")
    print(f"  {'-'*30} | {'-'*3} | {'-'*7} | {'-'*30}")
    for r in results:
        sev_str = ", ".join(f"{k}={v}" for k, v in r.get("by_severity", {}).items() if v > 0)
        status = "[OK]" if not r.get("error") else "[ERRO]"
        print(f"  {status} {r['name']:28s} | {r.get('findings', 0):3d} | {r.get('duration_ms', 0):6.0f}ms | {sev_str}")
    print(f"\n{'='*50}")
    print(f"  FINALIZADO em {elapsed:.0f}s")
    print(f"{'='*50}")


if __name__ == "__main__":
    asyncio.run(main())
