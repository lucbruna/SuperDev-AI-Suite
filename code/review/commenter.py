from __future__ import annotations

import logging
from typing import Any


class Commenter:
    """Adds review comments to code."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.code.review.commenter")

    def add_comment(self, file: str, line: int, message: str) -> dict[str, Any]:
        comment = {"file": file, "line": line, "message": message}
        self._log.info("Comment on %s:%d", file, line)
        return comment

    def resolve_comment(self, comment_id: str) -> bool:
        self._log.info("Resolving comment %s", comment_id)
        return True
