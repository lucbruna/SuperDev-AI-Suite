"""Validation processors."""

from __future__ import annotations

import re
from typing import Any

from data_intelligence.processing.base import ProcessingError, Processor

_EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")


class EmailValidator(Processor):
    """Validates the email format; raises ProcessingError when invalid."""

    name = "email_validator"

    def __init__(self, field: str = "email") -> None:
        self.field = field

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        value = record.get(self.field)
        if not isinstance(value, str) or not _EMAIL_RE.match(value.strip()):
            raise ProcessingError(f"invalid email: {value!r}")
        return record


class RequiredFieldValidator(Processor):
    """Raises ProcessingError when a required field is missing/empty."""

    name = "required"

    def __init__(self, fields: list[str]) -> None:
        self.fields = fields

    def apply(self, record: dict[str, Any]) -> dict[str, Any]:
        for field in self.fields:
            value = record.get(field)
            if value is None or value == "":
                raise ProcessingError(f"missing required field: {field}")
        return record
