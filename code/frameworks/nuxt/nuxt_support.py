from __future__ import annotations

import logging


class NuxtSupport:
    """Nuxt.js framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.nuxt")

    def detect(self, project_root: str) -> bool:
        import os
        return os.path.isfile(os.path.join(project_root, "nuxt.config.js")) or os.path.isfile(os.path.join(project_root, "nuxt.config.ts"))
