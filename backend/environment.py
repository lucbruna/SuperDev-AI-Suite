from __future__ import annotations

import os
from enum import StrEnum


class Environment(StrEnum):
    DEV = "dev"
    TEST = "test"
    STAGING = "staging"
    PRODUCTION = "production"


def get_environment() -> Environment:
    env_raw = os.getenv("APP_ENV", "dev").strip().lower()
    try:
        return Environment(env_raw)
    except ValueError:
        return Environment.DEV
