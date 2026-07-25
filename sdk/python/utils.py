"""Utility functions for the SuperDev Python SDK."""

from __future__ import annotations

import hashlib
import re
import time
from typing import Any


def retry(
    func: Any,
    max_retries: int = 3,
    delay: float = 1.0,
    backoff: float = 2.0,
    exceptions: tuple[type[Exception], ...] = (Exception,),
) -> Any:
    """Retry a function call with exponential backoff."""
    last_exc: Exception | None = None
    for attempt in range(max_retries + 1):
        try:
            return func()
        except exceptions as e:
            last_exc = e
            if attempt < max_retries:
                time.sleep(delay * (backoff ** attempt))
    raise last_exc  # type: ignore[misc]


def truncate(text: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(text) <= max_length:
        return text
    return text[: max_length - len(suffix)] + suffix


def slugify(text: str) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^\w\s-]", "", text)
    text = re.sub(r"[\s_]+", "-", text)
    text = re.sub(r"-+", "-", text)
    return text.strip("-")


def hash_content(content: str | bytes) -> str:
    if isinstance(content, str):
        content = content.encode("utf-8")
    return hashlib.sha256(content).hexdigest()


def parse_rate_limit_header(header: str) -> dict[str, int]:
    result: dict[str, int] = {}
    for part in header.split(","):
        part = part.strip()
        if "=" in part:
            key, value = part.split("=", 1)
            try:
                result[key.strip()] = int(value.strip())
            except ValueError:
                continue
    return result


def format_cost(amount: float, currency: str = "USD") -> str:
    if currency == "USD":
        return f"${amount:.4f}"
    return f"{amount:.4f} {currency}"


def format_tokens(count: int) -> str:
    if count >= 1_000_000:
        return f"{count / 1_000_000:.1f}M"
    if count >= 1_000:
        return f"{count / 1_000:.1f}K"
    return str(count)


def merge_dicts(base: dict[str, Any], override: dict[str, Any]) -> dict[str, Any]:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = merge_dicts(result[key], value)
        else:
            result[key] = value
    return result
