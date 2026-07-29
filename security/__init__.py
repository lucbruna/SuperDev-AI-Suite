"""SuperDev Security — vulnerability analysis, OWASP, SBOM, secrets detection, and dependency scanning."""

from __future__ import annotations

from .base import BaseCheck, SecurityFinding, SecurityReport, Severity
from .owasp.analyzer import OWASPAnalyzer
from .sbom.generator import SBOMGenerator
from .secrets_detector.detector import SecretsDetector
from .vulnerability_engine.engine import VulnerabilityEngine
from .dependency_scan.scanner import SecurityDependencyScanner as DependencyScanScanner

__all__ = [
    "BaseCheck", "SecurityFinding", "SecurityReport", "Severity",
    "OWASPAnalyzer", "SBOMGenerator", "SecretsDetector",
    "VulnerabilityEngine", "DependencyScanScanner",
]
