from __future__ import annotations

import logging
from typing import Any


class AnsibleRole:
    """Scaffolds and manages Ansible roles."""

    def __init__(self, name: str, base_dir: str = ".") -> None:
        self._log = logging.getLogger("superdev.devops.ansible.role")
        self.name = name
        self.base_dir = base_dir

    def scaffold(self) -> list[str]:
        raise NotImplementedError

    def add_task(self, name: str, module: str, **kwargs: Any) -> None:
        raise NotImplementedError

    def add_variable(self, name: str, value: Any) -> None:
        raise NotImplementedError

    def add_template(self, name: str, content: str) -> None:
        raise NotImplementedError

    def structure(self) -> dict[str, Any]:
        raise NotImplementedError
