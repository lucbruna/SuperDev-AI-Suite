"""
Utility Validators
"""
import re
from typing import Any


def is_email(value: str) -> bool:
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, value))

def is_url(value: str) -> bool:
    pattern = r'^https?://.+'
    return bool(re.match(pattern, value))

def is_strong_password(value: str) -> bool:
    if len(value) < 8:
        return False
    if not re.search(r'[A-Z]', value):
        return False
    if not re.search(r'[a-z]', value):
        return False
    return re.search(r'\d', value)

def is_ip(value: str) -> bool:
    pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    return bool(re.match(pattern, value))

def validate_required(value: Any) -> str | None:
    if value is None or value == "":
        return "This field is required"
    return None

def validate_min_length(value: str, min_len: int) -> str | None:
    if len(value) < min_len:
        return f"Minimum length is {min_len}"
    return None

def validate_max_length(value: str, max_len: int) -> str | None:
    if len(value) > max_len:
        return f"Maximum length is {max_len}"
    return None
