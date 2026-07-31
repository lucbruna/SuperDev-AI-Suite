"""Small helpers used across the demo project."""

import uuid


def generate_id() -> str:
    """Return a short unique id."""
    return str(uuid.uuid4())[:8]


def format_currency(value: float) -> str:
    """Format a number as USD currency."""
    return f"${value:.2f}"
