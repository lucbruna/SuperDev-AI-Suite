"""Security Engine orchestrator (Volume 16).

Coordenates:
  - 5 subsystems existentes: owasp, sbom, secrets_detector,
    vulnerability_engine, dependency_scan
  - 10 subsistemas do spec: encryption, hashing, signatures, certificates,
    vault, secrets, integrity, compliance, security_scan, threat_detection
"""

from __future__ import annotations

import asyncio
from typing import Any

from .security_config import SecurityConfig
from .security_context import SecurityContext
from .security_events import SecurityEventBus
from .security_logger import SecurityLogger
from .security_metrics import SecurityMetrics
from .security_registry import SecurityRegistry
from .security_runtime import SecurityRuntime
from .security_security import SecurityGuard


class SecurityEngine:
    """Central orchestrator for the Security Engine (Volume 16)."""

    subsystem_names = (
        "owasp",
        "sbom",
        "secrets_detector",
        "vulnerability_engine",
        "dependency_scan",
        "encryption",
        "hashing",
        "signatures",
        "certificates",
        "vault",
        "secrets",
        "integrity",
        "compliance",
        "security_scan",
        "threat_detection",
    )

    def __init__(self, config: SecurityConfig | None = None) -> None:
        self._config = config or SecurityConfig.default()
        self._event_bus = SecurityEventBus()
        self._logger = SecurityLogger(name="security-engine")
        self._metrics = SecurityMetrics()
        self._registry = SecurityRegistry()
        self._runtime = SecurityRuntime()
        self._guard = SecurityGuard()
        self._context = SecurityContext()
        self._running = False

        # Wired lazily so `security` imports stay optional for the rest of the suite.
        self._subsystems: dict[str, Any] = {}

    # -- lifecycle -----------------------------------------------------------

    async def start(self) -> None:
        if self._running:
            return
        self._running = True
        self._runtime.start()
        await self._event_bus.emit("security.engine.started", {"config": self._config})
        self._logger.info("SecurityEngine started")

    async def stop(self) -> None:
        if not self._running:
            return
        self._running = False
        await self._event_bus.emit("security.engine.stopped", {})
        self._logger.info("SecurityEngine stopped")

    # -- subsystem wiring ----------------------------------------------------

    def subsystems(self) -> dict[str, Any]:
        """Lazily instantiate every subsystem the first time they are used."""
        if self._subsystems:
            return self._subsystems
        builders: dict[str, Any] = {}
        # Existing subsystems (async analyzers).
        try:
            from .dependency_scan.scanner import SecurityDependencyScanner
            from .owasp.analyzer import OWASPAnalyzer
            from .sbom.generator import SBOMGenerator
            from .secrets_detector.detector import SecretsDetector
            from .vulnerability_engine.engine import VulnerabilityEngine

            builders.update(
                {
                    "owasp": OWASPAnalyzer(engine=self),
                    "sbom": SBOMGenerator(engine=self),
                    "secrets_detector": SecretsDetector(engine=self),
                    "vulnerability_engine": VulnerabilityEngine(engine=self),
                    "dependency_scan": SecurityDependencyScanner(engine=self),
                }
            )
        except TypeError:
            # Existing analyzers may not accept an engine kwarg — instantiate plainly.
            try:
                from .dependency_scan.scanner import SecurityDependencyScanner
                from .owasp.analyzer import OWASPAnalyzer
                from .sbom.generator import SBOMGenerator
                from .secrets_detector.detector import SecretsDetector
                from .vulnerability_engine.engine import VulnerabilityEngine

                builders.update(
                    {
                        "owasp": OWASPAnalyzer(),
                        "sbom": SBOMGenerator(),
                        "secrets_detector": SecretsDetector(),
                        "vulnerability_engine": VulnerabilityEngine(),
                        "dependency_scan": SecurityDependencyScanner(),
                    }
                )
            except (ImportError, ModuleNotFoundError):  # pragma: no cover
                pass

        # New spec subsystems (all accept engine kwarg).
        try:
            from .certificates.certificate_engine import CertificateEngine
            from .compliance.compliance_engine import ComplianceEngine
            from .encryption.encryption_engine import EncryptionEngine
            from .hashing.hashing_engine import HashingEngine
            from .integrity.integrity_engine import IntegrityEngine
            from .secrets.secrets_engine import SecretsEngine
            from .security_scan.scan_engine import SecurityScanEngine
            from .signatures.signature_engine import SignatureEngine
            from .threat_detection.threat_detection_engine import ThreatDetectionEngine
            from .vault.vault_engine import VaultEngine

            builders.update(
                {
                    "encryption": EncryptionEngine(engine=self),
                    "hashing": HashingEngine(engine=self),
                    "signatures": SignatureEngine(engine=self),
                    "certificates": CertificateEngine(engine=self),
                    "vault": VaultEngine(engine=self),
                    "secrets": SecretsEngine(engine=self),
                    "integrity": IntegrityEngine(engine=self),
                    "compliance": ComplianceEngine(engine=self),
                    "security_scan": SecurityScanEngine(engine=self),
                    "threat_detection": ThreatDetectionEngine(engine=self),
                }
            )
        except (ImportError, ModuleNotFoundError):  # pragma: no cover
            pass

        for name, instance in builders.items():
            self._registry.register_artifact(name, instance)
        self._subsystems = builders
        return self._subsystems

    def __getattr__(self, name: str) -> Any:
        """Attribute access like ``engine.owasp`` resolves lazily."""
        subsystems = object.__getattribute__(self, "_subsystems")
        if name in subsystems:
            return subsystems[name]
        if name in self.subsystem_names:
            return self.subsystems()[name]
        raise AttributeError(f"SecurityEngine has no attribute {name!r}")

    # -- aggregate flows -----------------------------------------------------

    async def run_scan(self, target: str, _source: str = "") -> dict[str, Any]:
        """Run every available analyzer against a target and aggregate results."""
        self._runtime.record("scan")
        scan_id = self._context.begin_scan()
        self._metrics.increment("security.scans", labels={"target": target})
        results: dict[str, Any] = {"target": target, "scan_id": scan_id, "scans": {}}
        for name, subsystem in self.subsystems().items():
            analyzer = getattr(subsystem, "analyze", None)
            if analyzer is None:
                continue
            try:
                report = analyzer(target)
                if asyncio.iscoroutine(report):
                    report = await report
                if hasattr(report, "to_dict"):
                    results["scans"][name] = report.to_dict()
                else:
                    results["scans"][name] = report
            except Exception as exc:  # noqa: BLE001 - aggregate analyzer failures
                results["scans"][name] = {"error": str(exc)}
        results["total_findings"] = sum(
            s.get("total_findings", 0) for s in results["scans"].values()
        )
        await self._event_bus.emit(
            "security.scan.completed",
            {"target": target, "total_findings": results["total_findings"]},
        )
        return results

    def security_score(self) -> float:
        """Composite score from registered findings (1.0 = clean)."""
        summary = self._registry.summary()
        findings = summary.get("findings", 0)
        if findings == 0:
            return 1.0
        return max(0.0, round(1.0 - 0.05 * findings, 4))

    # -- status --------------------------------------------------------------

    def status(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "subsystems": sorted(self.subsystems().keys()),
            "registry": self._registry.summary(),
            "runtime": self._runtime.snapshot(),
            "metrics": self._metrics.snapshot(),
        }

    async def health(self) -> dict[str, Any]:
        return {
            "running": self._running,
            "uptime": self._runtime.uptime,
            "subsystems": len(self.subsystems()),
            "config": {
                "enabled": self._config.enabled,
                "encryption": self._config.encryption_algorithm,
                "hashing": self._config.hashing_algorithm,
                "compliance_standards": self._config.compliance_standards,
            },
        }

    # -- accessors -----------------------------------------------------------

    @property
    def config(self) -> SecurityConfig:
        return self._config

    @property
    def event_bus(self) -> SecurityEventBus:
        return self._event_bus

    @property
    def logger(self) -> SecurityLogger:
        return self._logger

    @property
    def metrics(self) -> SecurityMetrics:
        return self._metrics

    @property
    def registry(self) -> SecurityRegistry:
        return self._registry

    @property
    def runtime(self) -> SecurityRuntime:
        return self._runtime

    @property
    def guard(self) -> SecurityGuard:
        return self._guard

    @property
    def context(self) -> SecurityContext:
        return self._context

    @property
    def is_running(self) -> bool:
        return self._running


__all__ = ["SecurityEngine"]
