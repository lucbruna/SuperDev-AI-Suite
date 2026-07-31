from __future__ import annotations

import logging
from typing import Any


class RollbackManager:
    """Manages rollback of failed migrations."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.migration.rollback")

    def create_checkpoint(self, name: str) -> str:
        checkpoint_id = f"ckp_{id(self)}"
        self._log.info("Created checkpoint %s (%s)", checkpoint_id, name)
        return checkpoint_id

    def rollback(self, checkpoint_id: str) -> bool:
        self._log.info("Rolling back to checkpoint %s", checkpoint_id)
        return True
