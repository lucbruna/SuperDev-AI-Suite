"""Teste do SBOM Generator contra o projeto SuperDev."""

import asyncio
import json
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def main():
    root = os.path.dirname(os.path.abspath(__file__))
    sep = "=" * 60
    print(sep)
    print("  SBOM GENERATOR - TESTE")
    print(f"  Target: {root}")
    print(sep)

    from security.sbom.generator import SBOMGenerator

    generator = SBOMGenerator()
    result = await generator.analyze(root)

    sbom = result.metadata.get("sbom", {}) if result.metadata else {}

    print(f"\n  Status: {'OK' if not result.error else 'ERRO'}")
    if result.error:
        print(f"  Erro: {result.error}")
        return

    print(f"  Duracao: {result.scan_duration_ms:.0f}ms")
    print(f"  Total components: {sbom.get('dependencies_count', 0)}")
    print(f"  Formato: {sbom.get('bomFormat', '?')} v{sbom.get('specVersion', '?')}")

    # Project info
    meta = sbom.get("metadata", {})
    comp = meta.get("component", {})
    print(f"\n{sep}")
    print("  PROJETO")
    print(sep)
    print(f"  Nome:    {comp.get('name', '?')}")
    print(f"  Versao:  {comp.get('version', '?')}")
    print(f"  Tipo:    {comp.get('type', '?')}")
    print(f"  Gerado:  {meta.get('timestamp', '?')}")

    # Dependencies by ecosystem
    components = sbom.get("components", [])
    ecosystems = {}
    for c in components:
        eco = c.get("ecosystem", "unknown")
        if eco not in ecosystems:
            ecosystems[eco] = []
        ecosystems[eco].append(c)

    print(f"\n{sep}")
    print("  DEPENDENCIAS POR ECOSYSTEM")
    print(sep)
    for eco, deps in sorted(ecosystems.items()):
        print(f"\n  [{eco.upper()}] {len(deps)} packages")
        for dep in sorted(deps, key=lambda d: d.get("name", ""))[:10]:
            name = dep.get("name", "?")
            ver = dep.get("version", "?")
            purl = dep.get("purl", "")
            print(f"    {name:40s} @ {ver:15s}  {purl}")
        if len(deps) > 10:
            print(f"    ... e mais {len(deps) - 10} packages")

    # Statistics
    print(f"\n{sep}")
    print("  ESTATISTICAS")
    print(sep)
    total = len(components)
    print(f"  Total componentes: {total}")
    for eco, count in sorted(ecosystems.items(), key=lambda x: -len(x[1])):
        print(f"    {eco:20s}: {len(count)}")

    # Raw SBOM (truncated)
    print(f"\n{sep}")
    print("  RAW SBOM (primeiros 30 componentes)")
    print(sep)
    simplified = []
    for c in components[:30]:
        simplified.append({
            "name": c.get("name"),
            "version": c.get("version"),
            "ecosystem": c.get("ecosystem"),
            "purl": c.get("purl"),
        })
    print(json.dumps(simplified, indent=2, ensure_ascii=False))

    if len(components) > 30:
        print(f"\n  ... e mais {len(components) - 30} componentes")

    print(f"\n{sep}")
    print(f"  SBOM GERADO - {total} components em {result.scan_duration_ms:.0f}ms")
    print(sep)


if __name__ == "__main__":
    asyncio.run(main())
