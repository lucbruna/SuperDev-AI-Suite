from __future__ import annotations

import logging


class NextSupport:
    """Next.js framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.next")

    def detect(self, project_root: str) -> bool:
        import os
        pkg = os.path.join(project_root, "package.json")
        if not os.path.isfile(pkg):
            return False
        try:
            with open(pkg) as f:
                import json
                data = json.load(f)
            return "next" in data.get("dependencies", {}) or "next" in data.get("devDependencies", {})
        except Exception:
            return False
