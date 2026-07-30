from __future__ import annotations

from typing import Any

from .client import BaseClient


class AuthClient(BaseClient):
    """Authentication and authorization client for the API."""

    def login(self, username: str, password: str, **kwargs: Any) -> dict[str, Any]:
        body = {"username": username, "password": password, "grant_type": "password"}
        result = self.request("POST", "/auth/login", body=body, **kwargs)
        if isinstance(result, dict) and "access_token" in result:
            self.set_token(result["access_token"])
        return result  # type: ignore[return-value]

    def login_with_api_key(self, api_key: str) -> dict[str, Any]:
        self.set_api_key(api_key)
        result = self.request("POST", "/auth/api-key", body={"api_key": api_key})
        if isinstance(result, dict) and "access_token" in result:
            self.set_token(result["access_token"])
        return result  # type: ignore[return-value]

    def mfa_verify(self, code: str, temp_token: str, **kwargs: Any) -> dict[str, Any]:
        body = {"code": code, "temp_token": temp_token}
        result = self.request("POST", "/auth/mfa/verify", body=body, **kwargs)
        if isinstance(result, dict) and "access_token" in result:
            self.set_token(result["access_token"])
        return result  # type: ignore[return-value]

    def refresh(self, refresh_token: str, **kwargs: Any) -> dict[str, Any]:
        body = {"refresh_token": refresh_token}
        result = self.request("POST", "/auth/refresh", body=body, **kwargs)
        if isinstance(result, dict) and "access_token" in result:
            self.set_token(result["access_token"])
        return result  # type: ignore[return-value]

    def logout(self, **kwargs: Any) -> dict[str, Any]:
        result = self.request("POST", "/auth/logout", **kwargs)
        self._access_token = None
        return result  # type: ignore[return-value]

    def me(self, **kwargs: Any) -> dict[str, Any]:
        return self.request("GET", "/auth/me", **kwargs)  # type: ignore[return-value]

    def change_password(self, old_password: str, new_password: str, **kwargs: Any) -> dict[str, Any]:
        body = {"old_password": old_password, "new_password": new_password}
        return self.request("POST", "/auth/change-password", body=body, **kwargs)  # type: ignore[return-value]

    def check_permission(self, permission: str, resource: str = "", **kwargs: Any) -> dict[str, Any]:
        body = {"permission": permission, "resource": resource}
        return self.request("POST", "/auth/check-permission", body=body, **kwargs)  # type: ignore[return-value]
