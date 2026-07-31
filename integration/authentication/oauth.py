from __future__ import annotations

import logging
import secrets
from typing import Any


class OAuthProvider:
    """OAuth2-style provider: issues authorization codes and exchanges them
    for access tokens (offline simulation of the authorization code flow).
    """

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.integration.auth.oauth")
        self._clients: dict[str, str] = {}  # client_id -> client_secret
        self._codes: dict[str, str] = {}  # code -> client_id
        self._tokens: dict[str, str] = {}  # token -> client_id

    def register_client(self, client_id: str, client_secret: str) -> None:
        self._clients[client_id] = client_secret

    def authorize(self, client_id: str) -> str:
        """Returns an authorization code for a registered client."""
        if client_id not in self._clients:
            raise KeyError(f"unknown client {client_id!r}")
        code = secrets.token_hex(16)
        self._codes[code] = client_id
        return code

    def exchange(self, code: str, client_id: str, client_secret: str) -> str:
        """Exchanges an authorization code for an access token."""
        expected_secret = self._clients.get(client_id)
        if expected_secret is None or not secrets.compare_digest(expected_secret, client_secret):
            raise PermissionError("invalid client credentials")
        if self._codes.get(code) != client_id:
            raise PermissionError("invalid authorization code")
        self._codes.pop(code, None)
        token = f"oauth-{secrets.token_hex(16)}"
        self._tokens[token] = client_id
        return token

    def validate(self, token: str) -> str | None:
        return self._tokens.get(token)

    def revoke(self, token: str) -> bool:
        return self._tokens.pop(token, None) is not None

    def authorize_url(self, client_id: str, redirect_uri: str) -> str:
        return (f"/oauth/authorize?client_id={client_id}&redirect_uri={redirect_uri}")
