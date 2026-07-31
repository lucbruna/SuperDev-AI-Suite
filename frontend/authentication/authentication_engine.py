from __future__ import annotations

import hashlib
import hmac
import logging
import secrets
import time
from typing import Any


class AuthenticationEngine:
    """Handles login, registration, MFA and session management."""

    def __init__(self) -> None:
        self._log = logging.getLogger("superdev.frontend.authentication")
        self._users: dict[str, dict[str, Any]] = {}
        self._sessions: dict[str, dict[str, Any]] = {}
        self._devices: dict[str, list[dict[str, Any]]] = {}
        self._mfa_codes: dict[str, str] = {}
        self._session_ttl = 3600

    def register(self, email: str, password: str, name: str = "") -> dict[str, Any]:
        email = email.lower().strip()
        if email in self._users:
            raise ValueError(f"user already registered: {email}")
        user = {
            "email": email,
            "name": name or email.split("@")[0],
            "password_hash": self._hash(password),
            "mfa_enabled": False,
            "created_at": time.time(),
        }
        self._users[email] = user
        return {"email": email, "created": True}

    def login(self, email: str, password: str, device_id: str = "default") -> str:
        email = email.lower().strip()
        user = self._users.get(email)
        if user is None:
            raise PermissionError("invalid credentials")
        if not hmac.compare_digest(user["password_hash"], self._hash(password)):
            raise PermissionError("invalid credentials")
        if user.get("mfa_enabled"):
            raise PermissionError("MFA code required")
        return self._create_session(email, device_id)

    def verify_mfa(self, email: str, code: str) -> bool:
        expected = self._mfa_codes.get(email.lower())
        return expected is not None and hmac.compare_digest(expected, code)

    def enable_mfa(self, email: str) -> str:
        code = str(secrets.randbelow(900000) + 100000)
        self._mfa_codes[email.lower()] = code
        user = self._users.get(email.lower())
        if user is not None:
            user["mfa_enabled"] = True
        return code

    def _create_session(self, email: str, device_id: str) -> str:
        token = secrets.token_hex(32)
        self._sessions[token] = {
            "email": email,
            "device_id": device_id,
            "created_at": time.time(),
            "expires_at": time.time() + self._session_ttl,
        }
        self._devices.setdefault(email, []).append(
            {"device_id": device_id, "last_seen": time.time(), "token": token}
        )
        return token

    def validate(self, token: str) -> dict[str, Any]:
        session = self._sessions.get(token)
        if session is None:
            raise PermissionError("invalid session")
        if time.time() > session["expires_at"]:
            self._sessions.pop(token, None)
            raise PermissionError("session expired")
        return dict(session)

    def logout(self, token: str) -> bool:
        session = self._sessions.pop(token, None)
        if session is None:
            return False
        devices = self._devices.get(session["email"], [])
        self._devices[session["email"]] = [d for d in devices if d.get("token") != token]
        return True

    def list_sessions(self, email: str) -> list[dict[str, Any]]:
        return [
            {"token": token, **session}
            for token, session in self._sessions.items()
            if session["email"] == email
        ]

    def list_devices(self, email: str) -> list[dict[str, Any]]:
        return list(self._devices.get(email, []))

    def revoke_session(self, token: str) -> bool:
        return self._sessions.pop(token, None) is not None

    def revoke_device(self, email: str, device_id: str) -> int:
        devices = self._devices.get(email, [])
        targets = [d for d in devices if d["device_id"] == device_id]
        self._devices[email] = [d for d in devices if d["device_id"] != device_id]
        for device in targets:
            token = device.get("token")
            if isinstance(token, str):
                self._sessions.pop(token, None)
        return len(targets)

    @staticmethod
    def _hash(password: str) -> str:
        return hashlib.sha256(password.encode("utf-8")).hexdigest()
