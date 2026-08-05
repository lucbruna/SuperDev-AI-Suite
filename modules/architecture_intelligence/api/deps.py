"""API dependencies for the intelligence module.

Reuses the backend's ``get_current_user`` when the backend package is
available; degrades to an anonymous user when running standalone.
"""
from __future__ import annotations

from typing import Any


def get_optional_user() -> dict[str, Any] | None:
    try:
        from backend.dependencies import get_current_user

        return get_current_user()  # type: ignore[no-any-return]
    except Exception:
        return None
