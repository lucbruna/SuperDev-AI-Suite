"""Volume 16 — Security Engine: exemplo prático.

Demonstra o ciclo completo de segurança:

    criptografia -> hashing -> assinaturas -> vault -> integridade ->
    compliance -> threat detection -> scan agregado com risk score

Execute com:
    python examples/security-engine/main.py
"""

from __future__ import annotations

import asyncio
import sys
from pathlib import Path

# Ensure the SuperDev repo root is importable when run as a script.
_REPO_ROOT = Path(__file__).resolve().parents[2]
if str(_REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(_REPO_ROOT))

from security.security_engine import SecurityEngine  # noqa: E402


async def main() -> None:
    engine = SecurityEngine()
    await engine.start()

    # 1) Criptografia simétrica.
    key = engine.encryption.generate_key()
    payload = engine.encryption.encrypt("segredo do cliente", key)
    plaintext = engine.encryption.decrypt(payload, key)
    print(f"[encryption] {len(payload.ciphertext)} chars -> roundtrip ok: "
          f"{plaintext == 'segredo do cliente'}")

    # 2) Hashing (digest + senha com salt).
    digest = engine.hashing.digest("dado sensivel")
    pw = engine.hashing.hash_password("SenhaForte!123")
    print(f"[hashing] sha256={digest.digest[:12]}... | senha verificada: "
          f"{engine.hashing.verify_password('SenhaForte!123', pw)}")

    # 3) Assinaturas.
    signing_key = engine.signatures.generate_key()
    signed = engine.signatures.sign("manifesto-deploy", signing_key)
    valid_signature = engine.signatures.verify(
        "manifesto-deploy", signed.signature, signing_key
    )
    print(f"[signatures] assinatura válida: {valid_signature.valid}")

    # 4) Vault com TTL.
    engine.vault.store("db-password", "super-secreto", ttl_hours=2)
    print(f"[vault] db-password -> {engine.vault.get('db-password') == 'super-secreto'} "
          f"| rotação pendente: {len(engine.vault.due_for_rotation())}")

    # 5) Integridade.
    data = b"artefato-de-build"
    engine.integrity.register_and_verify("build-1.0.0", data)
    tampered = engine.integrity.verify("build-1.0.0", data + b"!")
    print(f"[integrity] artefato original: ok | após alteração: "
          f"{tampered.status}")

    # 6) Compliance SOC2.
    compliance = engine.compliance.evaluate(
        "SOC2",
        {"CC1": True, "CC2": True, "CC3": False, "CC4": True},
    )
    print(f"[compliance] SOC2 status={compliance.status.value} "
          f"score={compliance.score:.0%} gaps={compliance.gaps}")

    # 7) Threat detection.
    threats = engine.threat_detection.ingest(
        "login.failed", "api-gateway", {"username": "admin"}
    )
    for _ in range(4):
        engine.threat_detection.ingest("login.failed", "api-gateway", {"username": "admin"})
    threats += engine.threat_detection.ingest(
        "login.failed", "api-gateway", {"username": "admin"}
    )
    print(f"[threats] {len(threats)} ameaça(s) detectada(s) | "
          f"abertas: {engine.threat_detection.status()['open']}")

    # 8) Scan agregado com risk score.
    scan = await engine.security_scan.scan("demo-app")
    print(f"[scan] findings={scan.total_findings} | risk_score={scan.risk_score}/100")

    print(f"[score] security_score={engine.security_score()}")

    await engine.stop()
    return {"payload": payload, "threats": threats, "scan": scan}


if __name__ == "__main__":
    asyncio.run(main())
