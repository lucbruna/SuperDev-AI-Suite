from __future__ import annotations

import re
from dataclasses import dataclass, field
from typing import Any

from ..manifest.defaults import DEFAULT_CATEGORY


@dataclass
class ValidationResult:
    success: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)


class ManifestValidator:
    VALID_CATEGORIES = {"tool", "provider", "agent", "theme", "language", "other"}
    ALLOWED_PERMISSIONS = {
        "filesystem.read", "filesystem.write", "network.http", "network.all",
        "process.spawn", "clipboard.read", "clipboard.write", "ui.notification",
        "storage.local", "storage.global",
    }

    def __init__(self) -> None:
        self._semver_pattern = re.compile(
            r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)"
            r"(?:-((?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*)"
            r"(?:\.(?:0|[1-9]\d*|\d*[a-zA-Z-][0-9a-zA-Z-]*))*))?"
            r"(?:\+([0-9a-zA-Z-]+(?:\.[0-9a-zA-Z-]+)*))?$"
        )

    def validate(self, manifest: dict[str, Any]) -> ValidationResult:
        errors: list[str] = []
        warnings: list[str] = []

        name = manifest.get("name")
        if not name or not isinstance(name, str):
            errors.append("Manifest 'name' is required and must be a non-empty string")
        elif not name.strip():
            errors.append("Manifest 'name' must not be empty or whitespace-only")

        version = manifest.get("version")
        if not version or not isinstance(version, str):
            errors.append("Manifest 'version' is required and must be a string")
        elif not self._semver_pattern.match(version):
            errors.append(f"Manifest 'version' '{version}' is not valid semver")

        entrypoint = manifest.get("entrypoint")
        if entrypoint is not None:
            if not isinstance(entrypoint, str):
                errors.append("Manifest 'entrypoint' must be a string")
            elif not entrypoint.strip():
                errors.append("Manifest 'entrypoint' must not be empty")

        permissions = manifest.get("permissions", [])
        if not isinstance(permissions, list):
            errors.append("Manifest 'permissions' must be a list")
        else:
            for perm in permissions:
                if perm not in self.ALLOWED_PERMISSIONS:
                    warnings.append(f"Permission '{perm}' is not in the allowed list")

        category = manifest.get("category", DEFAULT_CATEGORY)
        if category not in self.VALID_CATEGORIES:
            warnings.append(f"Category '{category}' is not standard; valid: {self.VALID_CATEGORIES}")

        author = manifest.get("author")
        if author is not None and not isinstance(author, str):
            errors.append("Manifest 'author' must be a string")

        description = manifest.get("description")
        if description is not None and not isinstance(description, str):
            errors.append("Manifest 'description' must be a string")

        dependencies = manifest.get("dependencies")
        if dependencies is not None:
            if not isinstance(dependencies, list):
                errors.append("Manifest 'dependencies' must be a list")

        return ValidationResult(success=len(errors) == 0, errors=errors, warnings=warnings)
