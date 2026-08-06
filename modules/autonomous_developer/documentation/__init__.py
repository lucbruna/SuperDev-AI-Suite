"""Documentation package — deterministic markdown documentation generation."""
from __future__ import annotations

from modules.autonomous_developer.documentation.writer import (
    DocumentationResult,
    DocumentationWriter,
    generate_api_docs,
    generate_changelog_entry,
    generate_readme,
)

__all__ = [
    "DocumentationResult",
    "DocumentationWriter",
    "generate_api_docs",
    "generate_changelog_entry",
    "generate_readme",
]
