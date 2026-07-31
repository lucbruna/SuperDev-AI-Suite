from __future__ import annotations

import logging


class ExpressSupport:
    """Express.js framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.express")

    def detect(self, project_root: str) -> bool:
        import os
        pkg = os.path.join(project_root, "package.json")
        if not os.path.isfile(pkg):
            return False
        try:
            with open(pkg) as f:
                import json
                data = json.load(f)
            return "express" in data.get("dependencies", {}) or "express" in data.get("devDependencies", {})
        except Exception:
            return False
