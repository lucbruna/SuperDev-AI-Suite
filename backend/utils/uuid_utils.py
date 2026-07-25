import re
import uuid

UUID_REGEX: str = r"^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$"


def generate_uuid() -> str:
    return str(uuid.uuid4())


def is_valid_uuid(value: str) -> bool:
    return bool(re.match(UUID_REGEX, value, re.IGNORECASE))
