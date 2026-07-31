from __future__ import annotations

import logging


class FlaskSupport:
    """Flask framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.flask")

    def detect(self, project_root: str) -> bool:
        import os
        return os.path.isfile(os.path.join(project_root, "app.py")) or os.path.isfile(os.path.join(project_root, "wsgi.py"))
