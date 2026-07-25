"""Authentication utilities for the SuperDev Python SDK."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta, timezone
from typing import Any

from sdk.python.exceptions import AuthenticationError


@dataclass
class TokenPair:
    access_token: str
    refresh_token: str
    expires_at: datetime | None = None
    token_type: str = "Bearer"

    @property
    def is_expired(self) -> bool:
        if self.expires_at is None:
            return False
        return datetime.now(timezone.utc) >= self.expires_at

    def to_header(self) -> str:
        return f"{self.token_type} {self.access_token}"


class AuthManager:
    """Manages authentication state and token refresh."""

    def __init__(
        self,
        api_key: str | None = None,
        base_url: str = "",
    ) -> None:
        self.api_key = api_key
        self.base_url = base_url
        self._token_pair: TokenPair | None = None

    def get_headers(self) -> dict[str, str]:
        if self.api_key:
            return {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json",
            }
        if self._token_pair and not self._token_pair.is_expired:
            return {
                "Authorization": self._token_pair.to_header(),
                "Content-Type": "application/json",
            }
        raise AuthenticationError("No valid credentials available. Login first or provide an API key.")

    def set_tokens(self, access_token: str, refresh_token: str, expires_in: int = 3600) -> None:
        self._token_pair = TokenPair(
            access_token=access_token,
            refresh_token=refresh_token,
            expires_at=datetime.now(timezone.utc) + timedelta(seconds=expires_in),
        )

    def clear_tokens(self) -> None:
        self._token_pair = None

    @property
    def is_authenticated(self) -> bool:
        if self.api_key:
            return True
        return self._token_pair is not None and not self._token_pair.is_expired
