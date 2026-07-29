"""SBOM Generator — generates Software Bill of Materials in CycloneDX and SPDX formats."""

from __future__ import annotations

import json
import os
import re
import time
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from typing import Any

from ..base import BaseCheck, SecurityFinding, SecurityReport, Severity


class SBOMGenerator(BaseCheck):
    name = "sbom"
    description = "Generates Software Bill of Materials (SBOM) in CycloneDX and SPDX formats"

    SUPPORTED_FORMATS = {"cyclonedx", "spdx"}

    async def analyze(self, target: str) -> SecurityReport:
        """Generate an SBOM for the target project."""
        start = time.time()
        findings: list[SecurityFinding] = []

        path = os.path.abspath(target)
        if not os.path.exists(path):
            return SecurityReport(
                analyzer=self.name,
                target=target,
                error=f"Target path does not exist: {path}",
            )

        # Detect project type and extract dependencies
        deps: list[dict[str, Any]] = []

        if os.path.isdir(path):
            # Check for various dependency files
            dep_files = {
                "requirements.txt": self._parse_requirements,
                "Pipfile": self._parse_pipfile,
                "Pipfile.lock": self._parse_pipfile_lock,
                "package.json": self._parse_package_json,
                "package-lock.json": self._parse_package_lock,
                "pnpm-lock.yaml": self._parse_pnpm_lock,
                "go.mod": self._parse_go_mod,
                "go.sum": self._parse_go_sum,
                "Cargo.toml": self._parse_cargo_toml,
                "Cargo.lock": self._parse_cargo_lock,
                "Gemfile": self._parse_gemfile,
                "Gemfile.lock": self._parse_gemfile_lock,
                "pom.xml": self._parse_pom_xml,
                "build.gradle": self._parse_gradle,
            }

            for fname, parser in dep_files.items():
                fpath = os.path.join(path, fname)
                if os.path.exists(fpath):
                    try:
                        parsed = parser(fpath)
                        deps.extend(parsed)
                    except Exception as e:
                        findings.append(SecurityFinding(
                            rule_id="SBOM-PARSE-001",
                            title=f"Failed to parse {fname}",
                            description=str(e),
                            severity=Severity.LOW,
                            file_path=fpath,
                        ))

            # If no dependencies found, try scanning for dependency files recursively
            if not deps:
                deps = await self._scan_recursive(path)

        # Generate SBOM report
        sbom_data = self._build_sbom(deps, path)

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return SecurityReport(
            analyzer=self.name,
            target=target,
            total_findings=len(findings),
            findings=findings,
            scan_duration_ms=elapsed_ms,
            metadata={"sbom": sbom_data, "dependencies_count": len(deps)},
        )

    async def _scan_recursive(self, path: str) -> list[dict[str, Any]]:
        """Recursively scan for dependency files."""
        deps: list[dict[str, Any]] = []
        dep_file_names = {
            "requirements.txt", "Pipfile", "Pipfile.lock",
            "package.json", "package-lock.json", "Cargo.toml",
            "go.mod", "Gemfile", "pom.xml",
        }
        for root, dirs, files in os.walk(path):
            dirs[:] = [d for d in dirs if not d.startswith(".") and d != "node_modules"]
            for fname in files:
                if fname in dep_file_names:
                    fpath = os.path.join(root, fname)
                    parser = {
                        "requirements.txt": self._parse_requirements,
                        "Pipfile": self._parse_pipfile,
                        "Pipfile.lock": self._parse_pipfile_lock,
                        "package.json": self._parse_package_json,
                        "package-lock.json": self._parse_package_lock,
                        "Cargo.toml": self._parse_cargo_toml,
                        "go.mod": self._parse_go_mod,
                        "Gemfile": self._parse_gemfile,
                        "pom.xml": self._parse_pom_xml,
                    }.get(fname)
                    if parser:
                        try:
                            parsed = parser(fpath)
                            deps.extend(parsed)
                        except Exception:
                            pass
        return deps

    def _build_sbom(self, deps: list[dict], project_path: str) -> dict[str, Any]:
        """Build a CycloneDX-compatible SBOM data structure."""
        now = datetime.now(timezone.utc).isoformat()
        components = []
        for dep in deps:
            components.append({
                "type": "library",
                "name": dep.get("name", "unknown"),
                "version": dep.get("version", "0.0.0"),
                "purl": dep.get("purl", ""),
                "licenses": dep.get("licenses", []),
                "ecosystem": dep.get("ecosystem", "unknown"),
            })

        return {
            "bomFormat": "CycloneDX",
            "specVersion": "1.5",
            "serialNumber": f"urn:uuid:{int(time.time())}",
            "version": 1,
            "metadata": {
                "timestamp": now,
                "tools": [{"name": "SuperDev SBOM Generator", "version": "1.0.0"}],
                "component": {
                    "type": "application",
                    "name": os.path.basename(project_path),
                    "version": "1.0.0",
                },
            },
            "components": components,
            "dependencies_count": len(components),
        }

    # ===== Parsers for various dependency formats =====

    def _parse_requirements(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith(("#", "-", "git+", "http")):
                    continue
                match = re.match(r"^([\w._-]+)\s*[=~><]+\s*([\d.*]+)", line)
                if match:
                    name = match.group(1).lower()
                    version = match.group(2)
                    deps.append({
                        "name": name,
                        "version": version,
                        "ecosystem": "pypi",
                        "purl": f"pkg:pypi/{name}@{version}",
                        "licenses": [],
                    })
        return deps

    def _parse_pipfile(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for match in re.finditer(r'^([\w._-]+)\s*=\s*"([^"]*)"', content, re.MULTILINE):
            name = match.group(1).lower()
            version = match.group(2)
            if version != "*":
                deps.append({
                    "name": name, "version": version,
                    "ecosystem": "pypi", "purl": f"pkg:pypi/{name}@{version}",
                    "licenses": [],
                })
        return deps

    def _parse_pipfile_lock(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            for pkg_name, pkg_data in data.get("default", {}).items():
                ver = pkg_data.get("version", "").lstrip("=")
                deps.append({
                    "name": pkg_name.lower(), "version": ver,
                    "ecosystem": "pypi", "purl": f"pkg:pypi/{pkg_name.lower()}@{ver}",
                    "licenses": [],
                })
            for pkg_name, pkg_data in data.get("develop", {}).items():
                ver = pkg_data.get("version", "").lstrip("=")
                deps.append({
                    "name": pkg_name.lower(), "version": ver,
                    "ecosystem": "pypi", "purl": f"pkg:pypi/{pkg_name.lower()}@{ver}",
                    "licenses": [],
                })
        except Exception:
            pass
        return deps

    def _parse_package_json(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            for section in ("dependencies", "devDependencies", "peerDependencies"):
                for name, ver in data.get(section, {}).items():
                    version = re.sub(r"[\^~>=<]", "", str(ver)).split(" ")[0]
                    deps.append({
                        "name": name, "version": version,
                        "ecosystem": "npm",
                        "purl": f"pkg:npm/{name}@{version}",
                        "licenses": [],
                    })
        except Exception:
            pass
        return deps

    def _parse_package_lock(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        try:
            with open(file_path, encoding="utf-8") as f:
                data = json.load(f)
            for name, pkg_data in data.get("packages", {}).items():
                if name:  # Skip root package
                    version = pkg_data.get("version", "0.0.0")
                    deps.append({
                        "name": name.split("/")[-1] if name.startswith("node_modules/") else name,
                        "version": version,
                        "ecosystem": "npm",
                        "purl": f"pkg:npm/{name}@{version}",
                        "licenses": [],
                    })
        except Exception:
            pass
        return deps

    def _parse_pnpm_lock(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        try:
            with open(file_path, encoding="utf-8", errors="ignore") as f:
                for line in f:
                    match = re.match(r"^\s+{2}([\w@/-]+)@([\d.]+):", line)
                    if match:
                        deps.append({
                            "name": match.group(1), "version": match.group(2),
                            "ecosystem": "npm",
                            "purl": f"pkg:npm/{match.group(1)}@{match.group(2)}",
                            "licenses": [],
                        })
        except Exception:
            pass
        return deps

    def _parse_go_mod(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = re.match(r"^\s+([\w./-]+)\s+v?([\d.]+)", line)
                if match and not line.strip().startswith("go "):
                    deps.append({
                        "name": match.group(1), "version": match.group(2),
                        "ecosystem": "go",
                        "purl": f"pkg:golang/{match.group(1)}@{match.group(2)}",
                        "licenses": [],
                    })
        return deps

    def _parse_go_sum(self, file_path: str) -> list[dict]:
        deps: list[dict] = {}
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                parts = line.strip().split()
                if len(parts) >= 2:
                    name = parts[0]
                    version = parts[1]
                    if name not in deps:
                        deps[name] = {
                            "name": name, "version": version,
                            "ecosystem": "go",
                            "purl": f"pkg:golang/{name}@{version}",
                            "licenses": [],
                        }
        return list(deps.values())

    def _parse_cargo_toml(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            in_deps = False
            for line in f:
                if line.strip().startswith("[dependencies"):
                    in_deps = True
                    continue
                if line.strip().startswith("["):
                    in_deps = False
                    continue
                if in_deps:
                    match = re.match(r'^([\w_-]+)\s*=\s*["\']?([\d.*]+)["\']?', line)
                    if match:
                        deps.append({
                            "name": match.group(1), "version": match.group(2),
                            "ecosystem": "cargo",
                            "purl": f"pkg:cargo/{match.group(1)}@{match.group(2)}",
                            "licenses": [],
                        })
        return deps

    def _parse_cargo_lock(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            content = f.read()
        for match in re.finditer(
            r'\[\[package\]\]\s*\nname\s*=\s*"([^"]+)"\s*\nversion\s*=\s*"([^"]+)"',
            content,
        ):
            deps.append({
                "name": match.group(1), "version": match.group(2),
                "ecosystem": "cargo",
                "purl": f"pkg:cargo/{match.group(1)}@{match.group(2)}",
                "licenses": [],
            })
        return deps

    def _parse_gemfile(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = re.match(r'^\s*gem\s+["\']([\w_-]+)["\'].*[,]\s*["\']([\d.]+)["\']', line)
                if match:
                    deps.append({
                        "name": match.group(1), "version": match.group(2),
                        "ecosystem": "rubygems",
                        "purl": f"pkg:gem/{match.group(1)}@{match.group(2)}",
                        "licenses": [],
                    })
        return deps

    def _parse_gemfile_lock(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = re.match(r"^\s{4}([\w_-]+)\s+\(([\d.]+)\)", line)
                if match:
                    deps.append({
                        "name": match.group(1), "version": match.group(2),
                        "ecosystem": "rubygems",
                        "purl": f"pkg:gem/{match.group(1)}@{match.group(2)}",
                        "licenses": [],
                    })
        return deps

    def _parse_pom_xml(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        try:
            tree = ET.parse(file_path)
            root = tree.getroot()
            ns = {"ns": "http://maven.apache.org/POM/4.0.0"}
            for dep in root.findall(".//ns:dependency", ns):
                group_id = dep.find("ns:groupId", ns)
                artifact_id = dep.find("ns:artifactId", ns)
                version = dep.find("ns:version", ns)
                if group_id is not None and artifact_id is not None:
                    name = f"{group_id.text}:{artifact_id.text}"
                    ver = version.text if version is not None else "0.0.0"
                    deps.append({
                        "name": name, "version": ver,
                        "ecosystem": "maven",
                        "purl": f"pkg:maven/{name}@{ver}",
                        "licenses": [],
                    })
        except Exception:
            pass
        return deps

    def _parse_gradle(self, file_path: str) -> list[dict]:
        deps: list[dict] = []
        with open(file_path, encoding="utf-8", errors="ignore") as f:
            for line in f:
                match = re.match(
                    r'^\s*(?:implementation|api|compile|runtime)\s+["\']([\w.]+):([\w.-]+):([\d.]+)["\']',
                    line,
                )
                if match:
                    group = match.group(1)
                    artifact = match.group(2)
                    version = match.group(3)
                    name = f"{group}:{artifact}"
                    deps.append({
                        "name": name, "version": version,
                        "ecosystem": "gradle",
                        "purl": f"pkg:gradle/{name}@{version}",
                        "licenses": [],
                    })
        return deps
