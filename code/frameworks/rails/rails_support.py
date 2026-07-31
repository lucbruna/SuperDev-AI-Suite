from __future__ import annotations

import logging


class RailsSupport:
    """Ruby on Rails framework support."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.frameworks.rails")

    def detect(self, project_root: str) -> bool:
        import os
        return os.path.isfile(os.path.join(project_root, "Gemfile")) and os.path.isdir(os.path.join(project_root, "app"))
