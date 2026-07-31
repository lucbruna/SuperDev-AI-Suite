"""
Multi-Factor Authentication
"""
from typing import Dict, Any, Optional
from dataclasses import dataclass, field
from enum import Enum
import secrets
import hashlib


class MFAMethod(Enum):
    TOTP = "totp"
    SMS = "sms"
    EMAIL = "email"
    HARDWARE_KEY = "hardware_key"
    BACKUP_CODES = "backup_codes"


@dataclass
class MFAConfig:
    user_id: str
    methods: list = field(default_factory=list)
    primary_method: MFAMethod = MFAMethod.TOTP
    backup_codes: list = field(default_factory=list)
    is_enabled: bool = False


@dataclass
class MFAChallenge:
    challenge_id: str
    user_id: str
    method: MFAMethod
    code: str
    expires_at: Any = None
    attempts: int = 0
    max_attempts: int = 3
    verified: bool = False


class MFAManager:
    def __init__(self):
        self.configs: Dict[str, MFAConfig] = {}
        self.challenges: Dict[str, MFAChallenge] = {}
        
    def setup_mfa(self, user_id: str, method: MFAMethod) -> MFAConfig:
        config = MFAConfig(user_id=user_id, methods=[method], primary_method=method)
        self.configs[user_id] = config
        return config
        
    def enable_mfa(self, user_id: str) -> bool:
        config = self.configs.get(user_id)
        if config:
            config.is_enabled = True
            return True
        return False
        
    def disable_mfa(self, user_id: str) -> bool:
        config = self.configs.get(user_id)
        if config:
            config.is_enabled = False
            return True
        return False
        
    def generate_challenge(self, user_id: str, method: MFAMethod = None) -> MFAChallenge:
        config = self.configs.get(user_id)
        if not config:
            raise ValueError("MFA not configured for user")
        mfa_method = method or config.primary_method
        code = secrets.token_hex(4).upper()
        challenge = MFAChallenge(
            challenge_id=secrets.token_hex(16),
            user_id=user_id,
            method=mfa_method,
            code=code
        )
        self.challenges[challenge.challenge_id] = challenge
        return challenge
        
    def verify_challenge(self, challenge_id: str, code: str) -> bool:
        challenge = self.challenges.get(challenge_id)
        if not challenge or challenge.verified:
            return False
        challenge.attempts += 1
        if challenge.attempts > challenge.max_attempts:
            return False
        if challenge.code == code:
            challenge.verified = True
            return True
        return False
        
    def is_enabled(self, user_id: str) -> bool:
        config = self.configs.get(user_id)
        return config.is_enabled if config else False
        
    def get_config(self, user_id: str) -> Optional[MFAConfig]:
        return self.configs.get(user_id)
        
    def generate_backup_codes(self, user_id: str, count: int = 10) -> list:
        codes = [secrets.token_hex(4).upper() for _ in range(count)]
        config = self.configs.get(user_id)
        if config:
            config.backup_codes = codes
        return codes
