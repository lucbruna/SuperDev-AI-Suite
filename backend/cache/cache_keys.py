from typing import Union


def user_key(user_id: Union[str, int]) -> str:
    return f"superdev:user:{user_id}"


def project_key(project_id: Union[str, int]) -> str:
    return f"superdev:project:{project_id}"


def session_key(session_id: str) -> str:
    return f"superdev:session:{session_id}"


def permission_key(
    user_id: Union[str, int], resource: str
) -> str:
    return f"superdev:permission:{user_id}:{resource}"


def token_key(token: str) -> str:
    return f"superdev:token:{token}"


def config_key(module: str) -> str:
    return f"superdev:config:{module}"


def rate_limit_key(identifier: str) -> str:
    return f"superdev:ratelimit:{identifier}"
