import base64
import hashlib


def sha256_hash(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def md5_hash(value: str) -> str:
    """DEPRECATED: Use sha256_hash() instead. MD5 is cryptographically weak."""
    import warnings
    warnings.warn("md5_hash is deprecated, use sha256_hash instead", DeprecationWarning, stacklevel=2)
    return hashlib.md5(value.encode("utf-8")).hexdigest()


def base64_encode(value: str) -> str:
    return base64.b64encode(value.encode("utf-8")).decode("utf-8")


def base64_decode(value: str) -> str:
    return base64.b64decode(value.encode("utf-8")).decode("utf-8")
