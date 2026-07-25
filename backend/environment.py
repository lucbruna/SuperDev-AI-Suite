from __future__ import annotations

import os
from enum import Enum


class Environment(str, Enum):
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