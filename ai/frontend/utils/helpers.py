"""
Utility Helpers
"""
from typing import Any, Dict, List, Optional
import hashlib
import uuid
import json


def generate_id() -> str:
    return str(uuid.uuid4())
    
def hash_string(text: str) -> str:
    return hashlib.sha256(text.encode()).hexdigest()
    
def deep_merge(base: Dict, override: Dict) -> Dict:
    result = base.copy()
    for key, value in override.items():
        if key in result and isinstance(result[key], dict) and isinstance(value, dict):
            result[key] = deep_merge(result[key], value)
        else:
            result[key] = value
    return result
    
def get_nested(obj: Dict, path: str, default: Any = None) -> Any:
    keys = path.split(".")
    current = obj
    for key in keys:
        if isinstance(current, dict) and key in current:
            current = current[key]
        else:
            return default
    return current
    
def set_nested(obj: Dict, path: str, value: Any) -> None:
    keys = path.split(".")
    current = obj
    for key in keys[:-1]:
        if key not in current:
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value
    
def chunk_list(lst: List, size: int) -> List[List]:
    return [lst[i:i+size] for i in range(0, len(lst), size)]
    
def debounce(func, delay: int = 300):
    import time
    last_called = [0]
    def wrapper(*args, **kwargs):
        now = time.time() * 1000
        if now - last_called[0] >= delay:
            last_called[0] = now
            return func(*args, **kwargs)
    return wrapper
    
def throttle(func, limit: int = 300):
    import time
    last_called = [0]
    def wrapper(*args, **kwargs):
        now = time.time() * 1000
        if now - last_called[0] >= limit:
            last_called[0] = now
            return func(*args, **kwargs)
    return wrapper
    
def slugify(text: str) -> str:
    return text.lower().replace(" ", "-").replace("_", "-")
