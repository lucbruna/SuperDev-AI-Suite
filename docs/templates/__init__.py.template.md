"""{{PACKAGE_NAME}} — {{PACKAGE_DESCRIPTION}}.

{{PACKAGE_DOCSTRING_BODY}}

Subpackages:
- ``{{SUBPACKAGE}}``: {{SUBPACKAGE_DESCRIPTION}}
"""
from __future__ import annotations

__version__ = "{{VERSION}}"
__all__: list[str] = []

<!--
Template for package __init__.py files. Replace the {{PLACEHOLDERS}} with the
actual package name, description, subpackages, and version. Keep the
`from __future__ import annotations` import as the first statement.
-->