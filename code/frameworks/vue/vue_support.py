from __future__ import annotations

import logging


class VueSupport:
    """Vue.js framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.vue")

    def detect(self, project_root: str) -> bool:
        import os
        return os.path.isfile(os.path.join(project_root, "vue.config.js"))
