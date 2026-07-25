from __future__ import annotations

import re
from typing import Any


class BaseValidator:
    """Base validation utilities."""

    @staticmethod
    def email(value: str) -> bool:
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return bool(re.match(pattern, value))

    @staticmethod
    def password(value: str) -> tuple[bool, list[str]]:
        errors = []
        if len(value) < 8:
            errors.append("Password must be at least 8 characters")
        if not re.search(r'[A-Z]', value):
            errors.append("Password must contain at least one uppercase letter")
        if not re.search(r'[a-z]', value):
            errors.append("Password must contain at least one lowercase letter")
        if not re.search(r'\d', value):
            errors.append("Password must contain at least one digit")
        return len(errors) == 0, errors

    @staticmethod
    def username(value: str) -> bool:
        pattern = r'^[a-zA-Z0-9_-]{3,50}$'
        return bool(re.match(pattern, value))

    @staticmethod
    def slug(value: str) -> bool:
        pattern = r'^[a-z0-9-]+$'
        return bool(re.match(pattern, value))

    @staticmethod
    def url(value: str) -> bool:
        pattern = r'^https?://[^\s]+$'
        return bool(re.match(pattern, value))

    @staticmethod
    def min_length(value: str, min_len: int) -> bool:
        return len(value) >= min_len

    @staticmethod
    def max_length(value: str, max_len: int) -> bool:
        return len(value) <= max_len

    @staticmethod
    def not_empty(value: Any) -> bool:
        if isinstance(value, str):
            return len(value.strip()) > 0
        return value is not None


validator = BaseValidator()
