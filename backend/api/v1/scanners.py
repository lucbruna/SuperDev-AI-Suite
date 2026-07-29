"""FastAPI routes for all SuperDev scanners and security analyzers.

Exposes 8 scanners + 5 security modules as REST endpoints under /api/v1/scanners.
"""

from __future__ import annotations

import logging
import os
import time
from typing import Any

logger = logging.getLogger(__name__)

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel

from backend.dependencies import get_current_active_user

router = APIRouter(
    tags=["scanners"],
    dependencies=[Depends(get_current_active_user)],
)


# ─── Schemas ──────────────────────────────────────────────────────────────────

class ScanRequest(BaseModel):
    target: str = "."
    timeout: int = 30


class ScanFindingOut(BaseModel):
    rule_id: str
    title: str
    description: str
    severity: str
    file_path: str = ""
    line: int = 0
    column: int = 0
    snippet: str = ""
    recommendation: str = ""
    type: str = ""
    cve: str = ""
    cvss_score: float = 0.0


class ScanResponse(BaseModel):
    scanner: str
    target: str
    total_findings: int
    by_severity: dict[str, int]
    findings: list[ScanFindingOut]
    duration_ms: float
    error: str = ""


class ScannerInfo(BaseModel):
    name: str
    description: str
    available: bool


class ScannersListResponse(BaseModel):
    scanners: list[ScannerInfo]


class SecurityFindingOut(BaseModel):
    rule_id: str
    title: str
    description: str
    severity: str
    file_path: str = ""
    line: int = 0
    cve: str = ""
    cvss: float = 0.0
    recommendation: str = ""


class SecurityResponse(BaseModel):
    analyzer: str
    target: str
    total_findings: int
    by_severity: dict[str, int]
    findings: list[SecurityFindingOut]
    duration_ms: float
    error: str = ""
    metadata: dict[str, Any] = {}


# ─── Utils ────────────────────────────────────────────────────────────────────

def _finding_to_dict(f) -> dict:
    return {
        "rule_id": getattr(f, "rule_id", ""),
        "title": getattr(f, "title", ""),
        "description": getattr(f, "description", ""),
        "severity": getattr(f, "severity", "info").value if hasattr(f, "severity") else "info",
        "file_path": getattr(f, "file_path", ""),
        "line": getattr(f, "line", 0) or 0,
        "column": getattr(f, "column", 0) or 0,
        "snippet": getattr(f, "snippet", ""),
        "recommendation": getattr(f, "recommendation", ""),
        "type": getattr(f, "type", "").value if hasattr(f, "type") else "",
        "cve": getattr(f, "cve", ""),
        "cvss_score": getattr(f, "cvss_score", 0.0) or getattr(f, "cvss", 0.0),
    }


def _security_finding_to_dict(f) -> dict:
    return {
        "rule_id": getattr(f, "rule_id", ""),
        "title": getattr(f, "title", ""),
        "description": getattr(f, "description", ""),
        "severity": getattr(f, "severity", "info").value if hasattr(f, "severity") else "info",
        "file_path": getattr(f, "file_path", ""),
        "line": getattr(f, "line", 0) or 0,
        "cve": getattr(f, "cve", ""),
        "cvss": getattr(f, "cvss", 0.0),
        "recommendation": getattr(f, "recommendation", ""),
    }


async def run_scanner(name: str, scanner_class, target: str, timeout: int = 30) -> dict[str, Any]:
    """Instantiate and run a scanner, returning structured results."""
    import asyncio
    start = time.time()
    try:
        scanner = scanner_class()
        result = await asyncio.wait_for(scanner.scan(target), timeout=timeout)
        findings_out = [_finding_to_dict(f) for f in (result.findings or [])]
        by_severity = result.by_severity if hasattr(result, "by_severity") else {}
        return {
            "scanner": name,
            "target": getattr(result, "target", target),
            "total_findings": result.total_findings,
            "by_severity": by_severity,
            "findings": findings_out,
            "duration_ms": round((time.time() - start) * 1000, 2),
            "error": getattr(result, "error", ""),
        }
    except asyncio.TimeoutError:
        return {
            "scanner": name,
            "target": target,
            "total_findings": 0,
            "by_severity": {},
            "findings": [],
            "duration_ms": round((time.time() - start) * 1000, 2),
            "error": f"Scanner timed out after {timeout}s",
        }
    except Exception as e:
        return {
            "scanner": name,
            "target": target,
            "total_findings": 0,
            "by_severity": {},
            "findings": [],
            "duration_ms": round((time.time() - start) * 1000, 2),
            "error": str(e)[:200],
        }


async def run_security(name: str, analyzer_class, target: str, timeout: int = 30) -> dict[str, Any]:
    """Instantiate and run a security analyzer, returning structured results."""
    import asyncio
    start = time.time()
    try:
        analyzer = analyzer_class()
        result = await asyncio.wait_for(analyzer.analyze(target), timeout=timeout)
        findings_out = [_security_finding_to_dict(f) for f in (result.findings or [])]
        by_severity = result.by_severity if hasattr(result, "by_severity") else {}
        metadata = getattr(result, "metadata", {})
        return {
            "analyzer": name,
            "target": getattr(result, "target", target),
            "total_findings": result.total_findings,
            "by_severity": by_severity,
            "findings": findings_out,
            "duration_ms": round((time.time() - start) * 1000, 2),
            "error": getattr(result, "error", ""),
            "metadata": metadata,
        }
    except asyncio.TimeoutError:
        return {
            "analyzer": name,
            "target": target,
            "total_findings": 0,
            "by_severity": {},
            "findings": [],
            "duration_ms": round((time.time() - start) * 1000, 2),
            "error": f"Analyzer timed out after {timeout}s",
        }
    except Exception as e:
        return {
            "analyzer": name,
            "target": target,
            "total_findings": 0,
            "by_severity": {},
            "findings": [],
            "duration_ms": round((time.time() - start) * 1000, 2),
            "error": str(e)[:200],
            "metadata": {},
        }


# ─── Scanner Registry ─────────────────────────────────────────────────────────

# All available scanners with their metadata
SCANNER_REGISTRY: dict[str, dict[str, Any]] = {
    "filesystem": {
        "name": "filesystem",
        "description": "Analyzes file system structure, permissions, and security issues",
        "class": None,  # Lazy-imported
        "type": "scanner",
    },
    "source_code": {
        "name": "source_code",
        "description": "Analyzes source code for bugs, security issues, and best practices via AST",
        "class": None,
        "type": "scanner",
    },
    "dependencies": {
        "name": "dependencies",
        "description": "Scans project dependencies for known vulnerabilities and outdated packages",
        "class": None,
        "type": "scanner",
    },
    "docker": {
        "name": "docker",
        "description": "Analyzes Dockerfiles and docker-compose for security and best practices",
        "class": None,
        "type": "scanner",
    },
    "kubernetes": {
        "name": "kubernetes",
        "description": "Analyzes Kubernetes manifests for security and configuration issues",
        "class": None,
        "type": "scanner",
    },
    "terraform": {
        "name": "terraform",
        "description": "Analyzes Terraform HCL files for security, compliance, and best practices",
        "class": None,
        "type": "scanner",
    },
    "cloud": {
        "name": "cloud",
        "description": "Scans cloud provider configurations (AWS, Azure, GCP) for security misconfigurations",
        "class": None,
        "type": "scanner",
    },
    "secrets": {
        "name": "secrets",
        "description": "Detects hardcoded secrets, API keys, tokens, passwords, and sensitive data",
        "class": None,
        "type": "scanner",
    },
    "owasp": {
        "name": "owasp",
        "description": "OWASP Top 10 vulnerability analysis for source code",
        "class": None,
        "type": "security",
    },
    "secrets_detector": {
        "name": "secrets_detector",
        "description": "Advanced secrets detection with context analysis, entropy scoring, and validation",
        "class": None,
        "type": "security",
    },
    "vulnerability_engine": {
        "name": "vulnerability_engine",
        "description": "Aggregates, correlates, and prioritizes vulnerabilities from multiple sources",
        "class": None,
        "type": "security",
    },
    "dependency_scan": {
        "name": "dependency_scan",
        "description": "Scans project dependencies for known vulnerabilities and outdated packages",
        "class": None,
        "type": "security",
    },
    "sbom": {
        "name": "sbom",
        "description": "Generates Software Bill of Materials (SBOM) in CycloneDX format",
        "class": None,
        "type": "security",
    },
}


def _resolve_scanner_class(scanner_id: str) -> Any:
    """Lazy-import and resolve a scanner class by ID."""
    if scanner_id not in SCANNER_REGISTRY:
        return None

    entry = SCANNER_REGISTRY[scanner_id]
    if entry["class"] is not None:
        return entry["class"]

    # Lazy imports for each scanner
    imports = {
        "filesystem": "scanners.filesystem.scanner:FilesystemScanner",
        "source_code": "scanners.source_code.scanner:SourceCodeScanner",
        "dependencies": "scanners.dependencies.scanner:DependencyScanner",
        "docker": "scanners.docker.scanner:DockerScanner",
        "kubernetes": "scanners.kubernetes.scanner:KubernetesScanner",
        "terraform": "scanners.terraform.scanner:TerraformScanner",
        "cloud": "scanners.cloud.scanner:CloudScanner",
        "secrets": "scanners.secrets.scanner:SecretsScanner",
        "owasp": "security.owasp.analyzer:OWASPAnalyzer",
        "secrets_detector": "security.secrets_detector.detector:SecretsDetector",
        "vulnerability_engine": "security.vulnerability_engine.engine:VulnerabilityEngine",
        "dependency_scan": "security.dependency_scan.scanner:SecurityDependencyScanner",
        "sbom": "security.sbom.generator:SBOMGenerator",
    }

    import_path = imports.get(scanner_id)
    if not import_path:
        return None

    try:
        module_path, class_name = import_path.split(":")
        import importlib
        module = importlib.import_module(module_path)
        cls = getattr(module, class_name)
        entry["class"] = cls
        return cls
    except (ImportError, AttributeError) as e:
        logger.warning(
            "Failed to import scanner '%s' from %s: %s",
            scanner_id, import_path, e,
        )
        return None


# ─── Endpoints ────────────────────────────────────────────────────────────────

@router.get("", response_model=ScannersListResponse)
async def list_scanners() -> dict[str, Any]:
    """List all available scanners and security analyzers."""
    scanners = []
    for sid, info in SCANNER_REGISTRY.items():
        cls = _resolve_scanner_class(sid)
        scanners.append(ScannerInfo(
            name=sid,
            description=info["description"],
            available=cls is not None,
        ))
    return {"scanners": scanners}


@router.post("/{scanner_id}/scan")
async def run_scan(
    scanner_id: str,
    request: ScanRequest = ScanRequest(),
) -> dict[str, Any]:
    """Run a specific scanner against a target path."""
    cls = _resolve_scanner_class(scanner_id)
    if cls is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Scanner '{scanner_id}' not found. Use GET /api/v1/scanners to list available scanners.",
        )

    # Resolve absolute target path
    target = os.path.abspath(request.target)
    if not os.path.exists(target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target path does not exist: {target}",
        )

    entry = SCANNER_REGISTRY[scanner_id]
    if entry["type"] == "security":
        return await run_security(scanner_id, cls, target, request.timeout)
    else:
        return await run_scanner(scanner_id, cls, target, request.timeout)


@router.post("/all/scan")
async def run_all_scanners(
    request: ScanRequest = ScanRequest(),
) -> list[dict[str, Any]]:
    """Run all available scanners against a target path."""
    target = os.path.abspath(request.target)
    if not os.path.exists(target):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Target path does not exist: {target}",
        )

    results = []
    for sid in SCANNER_REGISTRY:
        cls = _resolve_scanner_class(sid)
        if cls is None:
            continue
        entry = SCANNER_REGISTRY[sid]
        if entry["type"] == "security":
            result = await run_security(sid, cls, target, request.timeout)
        else:
            result = await run_scanner(sid, cls, target, request.timeout)
        results.append(result)
    return results
