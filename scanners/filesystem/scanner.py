"""Filesystem Scanner — analyzes file system structure, permissions, and security."""

from __future__ import annotations

import os
import stat
import time

from ..base import BaseScanner, Finding, FindingType, ScanResult, Severity


class FilesystemScanner(BaseScanner):
    name = "filesystem"
    description = "Analyzes file system structure, permissions, and security issues"

    DANGEROUS_PERMISSIONS = {
        "world_writable": 0o002,
        "world_readable_secret": 0o004,
        "sticky_bit_missing": 0o1000,
    }

    SUSPICIOUS_FILES = {
        ".env": "Environment file with potential secrets",
        ".npmrc": "NPM config with potential tokens",
        ".netrc": "Network credentials file",
        "credentials.json": "Service account credentials",
        "id_rsa": "SSH private key",
        "config.json": "Configuration with potential secrets",
    }

    IGNORE_DIRS = {
        ".git", "__pycache__", "node_modules", ".next",
        ".venv", "venv", ".tox", ".egg-info", "dist", "build",
        ".mypy_cache", ".pytest_cache", ".ruff_cache",
    }

    async def scan(self, target: str) -> ScanResult:
        start = time.time()
        all_findings: list[Finding] = []

        path = os.path.abspath(target)
        if not os.path.exists(path):
            return ScanResult(
                scanner_name=self.name,
                target=target,
                error=f"Path does not exist: {path}",
                scan_duration_ms=0,
                timestamp=__import__("datetime").datetime.now().isoformat(),
            )

        for root, dirs, files in os.walk(path):
            # Skip ignored directories
            dirs[:] = [d for d in dirs if d not in self.IGNORE_DIRS]

            for name in dirs:
                full_path = os.path.join(root, name)
                try:
                    st = os.stat(full_path)
                    finding = self._check_permissions(full_path, st, is_dir=True)
                    if finding:
                        all_findings.append(finding)
                except OSError:
                    pass

            for name in files:
                full_path = os.path.join(root, name)
                try:
                    st = os.stat(full_path)

                    # Check permissions
                    finding = self._check_permissions(full_path, st, is_dir=False)
                    if finding:
                        all_findings.append(finding)

                    # Check for suspicious files
                    finding = self._check_suspicious(full_path, name)
                    if finding:
                        all_findings.append(finding)

                    # Check file size
                    finding = self._check_file_size(full_path, name, st)
                    if finding:
                        all_findings.append(finding)

                except OSError:
                    pass

        elapsed_ms = round((time.time() - start) * 1000, 2)
        return ScanResult(
            scanner_name=self.name,
            target=target,
            total_findings=len(all_findings),
            findings=all_findings,
            scan_duration_ms=elapsed_ms,
            timestamp=__import__("datetime").datetime.now().isoformat(),
        )

    def _check_permissions(
        self, path: str, st: os.stat_result, is_dir: bool,
    ) -> Finding | None:
        mode = st.st_mode
        perms = stat.S_IMODE(mode)

        # World-writable files
        if perms & 0o002:
            return Finding(
                rule_id="FS-PERM-001",
                title="World-writable file",
                description=f"File has world-writable permissions ({oct(perms)})",
                severity=Severity.HIGH,
                file_path=path,
                line=0,
                snippet=f"Permissions: {oct(perms)}",
                recommendation="Remove world-write permissions: chmod o-w <file>",
                type=FindingType.SECURITY,
            )

        # SUID/SGID binaries
        if not is_dir and (mode & stat.S_ISUID or mode & stat.S_ISGID):
            return Finding(
                rule_id="FS-PERM-002",
                title="SUID/SGID binary detected",
                description=f"File has SUID/SGID bit set ({oct(perms)})",
                severity=Severity.MEDIUM,
                file_path=path,
                line=0,
                snippet=f"Permissions: {oct(perms)}",
                recommendation="Remove SUID/SGID unless absolutely necessary",
                type=FindingType.SECURITY,
            )

        return None

    def _check_suspicious(self, path: str, name: str) -> Finding | None:
        if name in self.SUSPICIOUS_FILES:
            return Finding(
                rule_id="FS-SUS-001",
                title=f"Suspicious file: {name}",
                description=self.SUSPICIOUS_FILES[name],
                severity=Severity.HIGH,
                file_path=path,
                line=0,
                recommendation="Ensure this file is in .gitignore and not committed",
                type=FindingType.SECRET,
            )
        return None

    def _check_file_size(
        self, path: str, name: str, st: os.stat_result,
    ) -> Finding | None:
        size_mb = st.st_size / (1024 * 1024)
        if size_mb > 100:
            return Finding(
                rule_id="FS-SIZE-001",
                title=f"Large file: {name} ({size_mb:.1f} MB)",
                description="File exceeds recommended size limit of 100 MB",
                severity=Severity.LOW,
                file_path=path,
                recommendation="Consider using Git LFS or splitting the file",
                type=FindingType.PERFORMANCE,
            )
        return None
