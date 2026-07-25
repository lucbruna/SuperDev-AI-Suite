import random
import re
import string
import unicodedata


def slugify(value: str) -> str:
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = re.sub(r"[^\w\s-]", "", value).strip().lower()
    value = re.sub(r"[-\s]+", "-", value)
    return value.strip("-")


def truncate(value: str, max_length: int = 100, suffix: str = "...") -> str:
    if len(value) <= max_length:
        return value
    if max_length <= len(suffix):
        return suffix[:max_length]
    
    # Target length without suffix
    target_len = max_length - len(suffix)
    truncated = value[:target_len]
    
    # Find last space to break at word boundary
    last_space = truncated.rfind(" ")
    if last_space > 0:
        # Keep the space before the suffix
        truncated = truncated[:last_space + 1]
    
    return truncated + suffix


def camel_to_snake(value: str) -> str:
    pattern = re.compile(r"(?<!^)(?=[A-Z])")
    return pattern.sub("_", value).lower()


def snake_to_camel(value: str) -> str:
    components = value.split("_")
    return components[0] + "".join(x.title() for x in components[1:])


def random_string(length: int = 32) -> str:
    chars = string.ascii_letters + string.digits
    return "".join(random.choices(chars, k=length))
