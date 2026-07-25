from __future__ import annotations

import platform
import sys
from typing import Any


class CompatibilityValidator:
    MIN_PYTHON = (3, 11)
    MIN_SUPERDEV = (5, 0, 0)
    SUPPORTED_PLATFORMS = {"windows", "linux", "darwin", "win32", "win64"}

    def check(self, manifest: dict[str, Any]) -> list[tuple[str, bool, str]]:
        results: list[tuple[str, bool, str]] = []

        python_version = sys.version_info[:2]
        if python_version >= self.MIN_PYTHON:
            results.append((
                "python_version", True,
                f"Python {python_version[0]}.{python_version[1]} >= {self.MIN_PYTHON[0]}.{self.MIN_PYTHON[1]}"
            ))
        else:
            results.append((
                "python_version", False,
                f"Python {python_version[0]}.{python_version[1]} < {self.MIN_PYTHON[0]}.{self.MIN_PYTHON[1]}"
            ))

        superdev_version_str = manifest.get("superdev_version")
        if superdev_version_str:
            try:
                parts = tuple(int(x) for x in superdev_version_str.split(".")[:3])
                if parts >= self.MIN_SUPERDEV:
                    results.append((
                        "superdev_version", True,
                        f"SuperDev {superdev_version_str} >= {'.'.join(str(x) for x in self.MIN_SUPERDEV)}"
                    ))
                else:
                    results.append((
                        "superdev_version", False,
                        f"SuperDev {superdev_version_str} < {'.'.join(str(x) for x in self.MIN_SUPERDEV)}"
                    ))
            except ValueError:
                results.append(("superdev_version", False, f"Invalid superdev_version: {superdev_version_str}"))
        else:
            results.append(("superdev_version", True, "No superdev_version specified, assuming compatible"))

        required_platform = manifest.get("platform")
        if required_platform:
            current_platform = platform.system().lower()
            if current_platform in self.SUPPORTED_PLATFORMS:
                current_platform = current_platform.replace("win32", "windows").replace("win64", "windows")
            if required_platform.lower() == current_platform:
                results.append(("platform", True, f"Platform '{current_platform}' matches required '{required_platform}'"))
            else:
                results.append(("platform", False, f"Platform '{current_platform}' does not match required '{required_platform}'"))
        else:
            results.append(("platform", True, "No platform restriction specified"))

        extra_requires = manifest.get("extra_requires", {})
        if isinstance(extra_requires, dict):
            for extra_name, extra_version in extra_requires.items():
                try:
                    __import__(extra_name)
                    results.append((f"extra_{extra_name}", True, f"Extra dependency '{extra_name}' is available"))
                except ImportError:
                    results.append((f"extra_{extra_name}", False, f"Extra dependency '{extra_name}' is not installed"))

        return results
