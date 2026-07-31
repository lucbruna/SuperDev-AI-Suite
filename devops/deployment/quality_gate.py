"""Quality gate for the DevOps flow — blocks deploys below quality standards.

Conecta o ``QualityEngine`` (Volume 15) ao fluxo de deploy do DevOps:

    DevOpsEngine.deploy_with_quality("api", "production", signals=...)
        └── DevOpsQualityGate.check_deployment(...)
              └── QualityEngine.evaluate_production_gate(...)
                    └── approved  -> deploy prossegue
                    └── blocked   -> deploy bloqueado (com motivos)

O gate é carregado de forma preguiçosa e falha de forma segura: se o módulo
``quality`` não estiver disponível, o gate retorna ``available=False`` (modo
"não bloqueia") em vez de quebrar o pipeline.
"""

from __future__ import annotations

import asyncio
from typing import Any


class DevOpsQualityGate:
    """Adapter do production gate do QualityEngine para o fluxo DevOps."""

    def __init__(self) -> None:
        self._engine: Any | None = None
        self._load_error: str | None = None

    # -- lazy loading --------------------------------------------------------

    def _quality_engine(self) -> Any | None:
        """Return the shared QualityEngine instance (created on first use)."""
        if self._engine is not None or self._load_error is not None:
            return self._engine
        try:
            from quality.quality_engine import QualityEngine

            self._engine = QualityEngine()
        except (ImportError, ModuleNotFoundError) as exc:  # pragma: no cover
            self._load_error = str(exc)
            self._engine = None
        return self._engine

    # -- gate evaluation -----------------------------------------------------

    async def evaluate(
        self,
        target: str,
        signals: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Evaluate the production gate for a deployment target.

        Returns a decision dict with ``decision`` in
        {"approved", "blocked", "unavailable"}.
        """
        engine = self._quality_engine()
        if engine is None:
            return {
                "available": False,
                "target": target,
                "decision": "unavailable",
                "blocked_reasons": [f"quality module unavailable: {self._load_error}"],
                "checks": [],
            }
        await engine.start()
        try:
            gate = await engine.evaluate_production_gate(
                target, dict(signals or {})
            )
            return {
                "available": True,
                "target": gate["target"],
                "decision": gate["decision"],
                "quality_score": gate["quality_score"],
                "blocked_reasons": gate["blocked_reasons"],
                "checks": gate["checks"],
                "gate_id": gate["gate_id"],
            }
        finally:
            await engine.stop()

    # -- synchronous helper (guards the deploy step) -------------------------

    def guard_deploy(
        self,
        target: str,
        signals: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """Sync wrapper for the gate check — returns blocked=True/False.

        Uses ``asyncio.run`` (only called from sync contexts, e.g. the
        synchronous deploy flow).
        """
        return asyncio.run(self.evaluate(target, signals))

    # -- status --------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "available": self._engine is not None,
            "load_error": self._load_error,
        }
