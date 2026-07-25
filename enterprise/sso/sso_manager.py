from __future__ import annotations as __

import asyncio
from typing import Dict, Any, Optional
from uuid import uuid4

from .saml_provider import SAMLProvider
from .oidc_provider import OIDCProvider
from .ldap_provider import LDAPProvider

from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    provider: str
    groups: list[str] = []


class SSOManager:
    def __init__(self) -> None:
        self._providers: Dict[str, Any] = {}
        self._configs: Dict[str, Dict[str, Any]] = {}

    async def configure(
        self, provider: str, config: Dict[str, Any]
    ) -> None:
        await asyncio.sleep(0.01)
        provider_lower = provider.lower()

        if provider_lower == "saml":
            self._providers[provider_lower] = SAMLProvider(**config)
        elif provider_lower == "oidc":
            self._providers[provider_lower] = OIDCProvider(**config)
        elif provider_lower == "ldap":
            self._providers[provider_lower] = LDAPProvider(**config)
        else:
            raise ValueError(f"Unsupported SSO provider: {provider}")

        self._configs[provider_lower] = config

    async def get_auth_url(
        self, provider: str, redirect_uri: str = ""
    ) -> str:
        await asyncio.sleep(0.01)
        prov = self._get_provider(provider)

        if isinstance(prov, SAMLProvider):
            return await prov.get_auth_url()
        elif isinstance(prov, OIDCProvider):
            return await prov.get_auth_url(redirect_uri=redirect_uri)
        elif isinstance(prov, LDAPProvider):
            raise ValueError("LDAP does not support auth URLs")

        raise ValueError(f"Provider {provider} not configured")

    async def handle_callback(
        self, provider: str, code: str = "", state: str = "", response: Optional[Dict[str, Any]] = None
    ) -> UserInfo:
        await asyncio.sleep(0.02)
        prov = self._get_provider(provider)

        if isinstance(prov, SAMLProvider):
            user_info = await prov.handle_callback(response or {})
        elif isinstance(prov, OIDCProvider):
            tokens = await prov.handle_callback(code)
            user_info = await prov.get_user_info(tokens.access_token)
        elif isinstance(prov, LDAPProvider):
            raise ValueError("LDAP does not support callback flow")

        return UserInfo(
            id=user_info.id,
            email=user_info.email,
            name=user_info.name,
            provider=provider,
            groups=user_info.groups,
        )

    async def get_user_info(
        self, provider: str, access_token: str = ""
    ) -> UserInfo:
        await asyncio.sleep(0.01)
        prov = self._get_provider(provider)

        if isinstance(prov, OIDCProvider):
            user_info = await prov.get_user_info(access_token)
        elif isinstance(prov, SAMLProvider):
            user_info = await prov.get_user_info(access_token)
        elif isinstance(prov, LDAPProvider):
            user_info = await prov.authenticate(
                access_token, ""
            )

        return UserInfo(
            id=user_info.id,
            email=user_info.email,
            name=user_info.name,
            provider=provider,
            groups=user_info.groups,
        )

    async def authenticate_ldap(
        self, username: str, password: str
    ) -> UserInfo:
        prov = self._get_provider("ldap")
        if not isinstance(prov, LDAPProvider):
            raise ValueError("LDAP provider not configured")

        user_info = await prov.authenticate(username, password)
        return UserInfo(
            id=user_info.id,
            email=user_info.email,
            name=user_info.name,
            provider="ldap",
            groups=user_info.groups,
        )

    def _get_provider(self, provider: str) -> Any:
        prov = self._providers.get(provider.lower())
        if not prov:
            raise ValueError(f"Provider {provider} not configured")
        return prov
