from __future__ import annotations

import logging
from typing import Any

from .api_key import APIKeyProvider
from .certificate import CertificateManager
from .jwt import JWTProvider
from .oauth import OAuthProvider
from .secret_manager import SecretManager
from .token_manager import TokenManager


class AuthEngine:
    """Facade for integration authentication: OAuth, JWT, API keys, tokens,
    certificates, and secrets.
    """

    def __init__(self, secret: str = "superdev-auth-secret", ttl: int = 3600) -> None:
        self._log = logging.getLogger("superdev.integration.auth")
        self.oauth = OAuthProvider()
        self.jwt = JWTProvider(secret)
        self.api_keys = APIKeyProvider()
        self.tokens = TokenManager(secret, ttl)
        self.certificates = CertificateManager()
        self.secrets = SecretManager()

    # --- Convenience passthroughs -------------------------------------------

    def authenticate(self, method: str, credentials: dict[str, Any]) -> str:
        """Authenticates using the given method and credentials.

        Methods: 'oauth' (code/client_id/client_secret), 'jwt' (token),
        'api_key' (api_key), 'token' (subject/scopes).
        """
        if method == "oauth":
            return self.oauth.exchange(
                credentials["code"], credentials["client_id"], credentials["client_secret"]
            )
        if method == "jwt":
            return credentials["token"]
        if method == "api_key":
            return credentials["api_key"]
        if method == "token":
            return self.tokens.issue(credentials["subject"], credentials.get("scopes"))
        raise ValueError(f"unknown auth method {method!r}")

    def validate(self, method: str, token: str) -> bool:
        if method == "api_key":
            return self.api_keys.validate(token) is not None
        if method == "jwt":
            return self.jwt.validate(token)
        if method == "oauth":
            return self.oauth.validate(token) is not None
        if method == "token":
            return self.tokens.subject(token) is not None
        raise ValueError(f"unknown auth method {method!r}")

    def stats(self) -> dict[str, Any]:
        return {
            "api_keys": self.api_keys.snapshot()["keys"],
            "secrets": self.secrets.snapshot()["secrets"],
            "certificates": len(self.certificates.list_names()),
        }
