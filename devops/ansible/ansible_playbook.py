from __future__ import annotations

import logging
from typing import Any


class AnsiblePlaybook:
    """Builds and validates Ansible playbooks."""

    def __init__(self, name: str) -> None:
        self._log = logging.getLogger("superdev.devops.ansible.playbook")
        self.name = name
        self._plays: list[dict[str, Any]] = []

    def add_play(self, hosts: str, tasks: list[dict[str, Any]], **kwargs: Any) -> AnsiblePlaybook:
        raise NotImplementedError

    def add_task(self, name: str, module: str, **kwargs: Any) -> AnsiblePlaybook:
        raise NotImplementedError

    def add_role(self, role: str, **kwargs: Any) -> AnsiblePlaybook:
        raise NotImplementedError

    def add_handler(self, name: str, module: str, **kwargs: Any) -> AnsiblePlaybook:
        raise NotImplementedError

    def render(self) -> str:
        raise NotImplementedError

    def validate(self) -> list[str]:
        raise NotImplementedError
