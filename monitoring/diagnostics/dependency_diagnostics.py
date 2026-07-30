from __future__ import annotations

from typing import Any

from .diagnostic_engine import DiagnosticResult


class DependencyDiagnostics:
    """Checks availability and versions of required dependencies."""

    @staticmethod
    def check_package(package_name: str, min_version: str = "") -> DiagnosticResult:
        try:
            import importlib.metadata
            try:
                version = importlib.metadata.version(package_name)
            except importlib.metadata.PackageNotFoundError:
                return DiagnosticResult(
                    check=f"package_{package_name}",
                    status="failed",
                    message=f"Package '{package_name}' is not installed",
                )

            if min_version:
                from packaging.version import Version
                if Version(version) < Version(min_version):
                    return DiagnosticResult(
                        check=f"package_{package_name}",
                        status="warning",
                        message=f"Package '{package_name}' version {version} < required {min_version}",
                        details={"installed": version, "required": min_version},
                    )

            return DiagnosticResult(
                check=f"package_{package_name}",
                status="passed",
                message=f"Package '{package_name}' version {version}",
                details={"version": version, "required": min_version},
            )
        except ImportError:
            return DiagnosticResult(
                check=f"package_{package_name}",
                status="warning",
                message="Cannot check package version (importlib.metadata not available)",
            )

    @staticmethod
    def check_python_version(required: str = "3.9") -> DiagnosticResult:
        import sys
        from packaging.version import Version
        current = f"{sys.version_info.major}.{sys.version_info.minor}"
        status = "passed" if Version(current) >= Version(required) else "failed"
        return DiagnosticResult(
            check="python_version",
            status=status,
            message=f"Python {current} (required >= {required})",
            details={"current": current, "required": required},
        )

    @staticmethod
    def check_module(module_name: str) -> DiagnosticResult:
        try:
            import importlib
            importlib.import_module(module_name)
            return DiagnosticResult(
                check=f"module_{module_name}",
                status="passed",
                message=f"Module '{module_name}' is available",
            )
        except ImportError:
            return DiagnosticResult(
                check=f"module_{module_name}",
                status="failed",
                message=f"Module '{module_name}' is not available",
            )
