"""Kubernetes Scanner — analyzes K8s manifests for security and configuration issues."""

from __future__ import annotations

import os
import re
import time
from typing import Any

from ..base import BaseScanner, Finding, FindingType, ScanResult, Severity


class KubernetesScanner(BaseScanner):
    name = "kubernetes"
    description = "Analyzes Kubernetes manifests for security and configuration issues"

    # Security checks for K8s resources
    CHECKS: list[dict[str, Any]] = [
        {
            "rule_id": "K8S-SEC-001",
            "title": "Container running as root",
            "check": lambda doc: (
                doc.get("kind") in ("Deployment", "StatefulSet", "DaemonSet", "Pod", "Job", "CronJob")
                and not _find_in_containers(doc, lambda c: c.get("securityContext", {}).get("runAsNonRoot"))
            ),
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "recommendation": "Set securityContext.runAsNonRoot: true and runAsUser: <non-zero>",
        },
        {
            "rule_id": "K8S-SEC-002",
            "title": "Privileged container",
            "check": lambda doc: _find_in_containers(doc, lambda c: c.get("securityContext", {}).get("privileged")),
            "severity": Severity.CRITICAL,
            "type": FindingType.SECURITY,
            "recommendation": "Remove privileged: true from securityContext",
        },
        {
            "rule_id": "K8S-SEC-003",
            "title": "Container with no resource limits",
            "check": lambda doc: not _find_in_containers(doc, lambda c: c.get("resources", {}).get("limits")),
            "severity": Severity.MEDIUM,
            "type": FindingType.PERFORMANCE,
            "recommendation": "Set resources.limits.cpu and resources.limits.memory",
        },
        {
            "rule_id": "K8S-SEC-004",
            "title": "No liveness/readiness probe",
            "check": lambda doc: not _find_in_containers(doc, lambda c: c.get("livenessProbe") or c.get("readinessProbe")),
            "severity": Severity.MEDIUM,
            "type": FindingType.BEST_PRACTICE,
            "recommendation": "Add livenessProbe and readinessProbe to containers",
        },
        {
            "rule_id": "K8S-SEC-005",
            "title": "Pod with hostNetwork access",
            "check": lambda doc: doc.get("spec", {}).get("hostNetwork") if doc.get("kind") == "Pod" else False,
            "severity": Severity.HIGH,
            "type": FindingType.SECURITY,
            "recommendation": "Avoid hostNetwork: true unless absolutely necessary",
        },
        {
            "rule_id": "K8S-SEC-006",
            "title": "Image tag is 'latest' or empty",
            "check": lambda doc: _find_in_containers(doc, lambda c: (c.get("image") or "").endswith(":latest") or ":" not in (c.get("image") or "")),
            "severity": Severity.MEDIUM,
            "type": FindingType.BEST_PRACTICE,
            "recommendation": "Pin a specific image version instead of 'latest'",
        },
        {
            "rule_id": "K8S-CONF-001",
            "title": "Service without selector",
            "check": lambda doc: doc.get("kind") == "Service" and not doc.get("spec", {}).get("selector"),
            "severity": Severity.MEDIUM,
            "type": FindingType.MISCONFIGURATION,
            "recommendation": "Add selector to match your pods",
        },
        {
            "rule_id": "K8S-CONF-002",
            "title": "PersistentVolumeClaim without storage class",
            "check": lambda doc: doc.get("kind") == "PersistentVolumeClaim" and not doc.get("spec", {}).get("storageClassName"),
            "severity": Severity.LOW,
            "type": FindingType.BEST_PRACTICE,
            "recommendation": "Specify storageClassName for predictable provisioning",
        },
        {
            "rule_id": "K8S-SEC-007",
            "title": "Secret with base64-encoded data in manifest",
            "check": lambda doc: doc.get("kind") == "Secret" and bool(doc.get("data")),
            "severity": Severity.HIGH,
            "type": FindingType.SECRET,
            "recommendation": "Use SealedSecrets, External Secrets Operator, or Helm with encrypted values",
        },
        {
            "rule_id": "K8S-SEC-008",
            "title": "CAP_SYS_ADMIN capability added",
            "check": lambda doc: _find_in_containers(doc, lambda c: any(
                cap.get("add") and "SYS_ADMIN" in str(cap.get("add"))
                for cap in [c.get("securityContext", {}).get("capabilities", {})]
            ) if c.get("securityContext", {}).get("capabilities") else False),
            "severity": Severity.CRITICAL,
            "type": FindingType.SECURITY,
            "recommendation": "Remove CAP_SYS_ADMIN capability. Use more specific capabilities.",
        },
    ]

    async def scan(self, target: str) -> ScanResult:
        start = time.time()
        all_findings: list[Finding] = []

        path = os.path.abspath(target)
        if os.path.isfile(path):
            findings = await self._scan_yaml(path)
            all_findings.extend(findings)
        elif os.path.isdir(path):
            for root, dirs, files in os.walk(path):
                dirs[:] = {d for d in dirs if not d.startswith(".") and d != "node_modules"}
                for fname in files:
                    if fname.endswith((".yaml", ".yml")):
                        fpath = os.path.join(root, fname)
                        findings = await self._scan_yaml(fpath)
                        all_findings.extend(findings)

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return ScanResult(
            scanner_name=self.name,
            target=target,
            total_findings=len(all_findings),
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
        )

    async def _scan_yaml(self, file_path: str) -> list[Finding]:
        findings: list[Finding] = []
        try:
            import yaml
            with open(file_path, encoding="utf-8") as f:
                docs = list(yaml.safe_load_all(f))
        except Exception:
            return findings

        for doc in docs:
            if not doc or not isinstance(doc, dict):
                continue
            for check in self.CHECKS:
                try:
                    if check["check"](doc):
                        kind = doc.get("kind", "Unknown")
                        name = doc.get("metadata", {}).get("name", "unnamed")
                        findings.append(Finding(
                            rule_id=check["rule_id"],
                            title=check["title"],
                            description=f"In {kind}/{name}",
                            severity=check["severity"],
                            file_path=file_path,
                            recommendation=check["recommendation"],
                            type=check["type"],
                        ))
                except Exception:
                    pass
        return findings


def _find_in_containers(doc: dict, predicate: Any) -> Any:
    """Check all containers in a pod spec against a predicate."""
    spec = doc.get("spec", {})
    if doc.get("kind") == "Pod":
        containers = spec.get("containers", [])
    elif doc.get("kind") in ("Deployment", "StatefulSet", "DaemonSet", "Job", "CronJob"):
        pod_spec = spec.get("template", {}).get("spec", {})
        containers = pod_spec.get("containers", [])
        if not containers:
            containers = spec.get("containers", [])
    else:
        return False

    for c in containers:
        if predicate(c):
            return True
    return False
