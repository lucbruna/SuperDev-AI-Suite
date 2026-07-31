from __future__ import annotations

import logging
from typing import Any


class AnsibleVault:
    """Encrypts and decrypts secrets with Ansible Vault."""

    def __init__(self, vault_password: str | None = None) -> None:
        self._log = logging.getLogger("superdev.devops.ansible.vault")
        self._vault_password = vault_password

    def encrypt_file(self, path: str, output: str | None = None) -> str:
        raise NotImplementedError

    def decrypt_file(self, path: str, output: str | None = None) -> str:
        raise NotImplementedError

    def encrypt_string(self, value: str, vault_id: str | None = None) -> str:
        raise NotImplementedError

    def rekey(self, path: str, new_password: str) -> bool:
        raise NotImplementedError

    def view(self, path: str) -> str:
        raise NotImplementedError
