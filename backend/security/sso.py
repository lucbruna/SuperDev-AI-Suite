from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any


class SSOProviderType(str, Enum):
    SAML = "saml"
    OIDC = "oidc"
    GOOGLE = "google"
    GITHUB = "github"
    MICROSOFT = "microsoft"


@dataclass
class SSOConfig:
    provider_type: SSOProviderType
    client_id: str
    client_secret: str
    metadata_url: str | None = None
    authorization_url: str | None = None
    token_url: str | None = None
    userinfo_url: str | None = None
    redirect_uri: str = "/api/v1/auth/sso/callback"
    scopes: list[str] = field(default_factory=lambda: ["openid", "email", "profile"])
    enabled: bool = True


@dataclass
class SSOUserInfo:
    subject: str
    email: str
    name: str | None = None
    given_name: str | None = None
    family_name: str | None = None
    picture: str | None = None
    groups: list[str] = field(default_factory=list)
    attributes: dict[str, Any] = field(default_factory=dict)


class BaseSSOProvider(ABC):
    """Abstract base class for SSO providers."""

    def __init__(self, config: SSOConfig):
        self.config = config

    @property
    @abstractmethod
    def provider_type(self) -> SSOProviderType:
        ...

    @abstractmethod
    async def get_authorization_url(self, state: str) -> str:
        ...

    @abstractmethod
    async def handle_callback(self, code: str, state: str) -> SSOUserInfo:
        ...

    @abstractmethod
    async def validate_token(self, token: str) -> SSOUserInfo | None:
        ...

    async def health_check(self) -> bool:
        return True


class OIDCProvider(BaseSSOProvider):
    """OpenID Connect provider implementation."""

    @property
    def provider_type(self) -> SSOProviderType:
        return SSOProviderType.OIDC

    async def get_authorization_url(self, state: str) -> str:
        import urllib.parse
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "response_type": "code",
            "scope": " ".join(self.config.scopes),
            "state": state,
        }
        return f"{self.config.authorization_url}?{urllib.parse.urlencode(params)}"

    async def handle_callback(self, code: str, state: str) -> SSOUserInfo:
        import httpx

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                self.config.token_url,
                data={
                    "grant_type": "authorization_code",
                    "code": code,
                    "redirect_uri": self.config.redirect_uri,
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                },
            )
            token_data = token_response.json()
            access_token = token_data.get("access_token")

            userinfo_response = await client.get(
                self.config.userinfo_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            userinfo = userinfo_response.json()

        return SSOUserInfo(
            subject=userinfo.get("sub", ""),
            email=userinfo.get("email", ""),
            name=userinfo.get("name"),
            given_name=userinfo.get("given_name"),
            family_name=userinfo.get("family_name"),
            picture=userinfo.get("picture"),
            groups=userinfo.get("groups", []),
            attributes=userinfo,
        )

    async def validate_token(self, token: str) -> SSOUserInfo | None:
        import httpx

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    self.config.userinfo_url,
                    headers={"Authorization": f"Bearer {token}"},
                )
                if response.status_code == 200:
                    userinfo = response.json()
                    return SSOUserInfo(
                        subject=userinfo.get("sub", ""),
                        email=userinfo.get("email", ""),
                        name=userinfo.get("name"),
                        groups=userinfo.get("groups", []),
                        attributes=userinfo,
                    )
        except Exception:
            pass
        return None


class SAMLProvider(BaseSSOProvider):
    """SAML 2.0 provider implementation (stub)."""

    @property
    def provider_type(self) -> SSOProviderType:
        return SSOProviderType.SAML

    async def get_authorization_url(self, state: str) -> str:
        return self.config.metadata_url or ""

    async def handle_callback(self, code: str, state: str) -> SSOUserInfo:
        raise NotImplementedError("SAML callback not implemented")

    async def validate_token(self, token: str) -> SSOUserInfo | None:
        return None


class GoogleProvider(OIDCProvider):
    """Google OAuth2/OIDC provider."""

    def __init__(self, client_id: str, client_secret: str, **kwargs):
        config = SSOConfig(
            provider_type=SSOProviderType.GOOGLE,
            client_id=client_id,
            client_secret=client_secret,
            authorization_url="https://accounts.google.com/o/oauth2/v2/auth",
            token_url="https://oauth2.googleapis.com/token",
            userinfo_url="https://www.googleapis.com/oauth2/v3/userinfo",
            scopes=["openid", "email", "profile"],
            **kwargs,
        )
        super().__init__(config)


class GitHubProvider(BaseSSOProvider):
    """GitHub OAuth provider."""

    @property
    def provider_type(self) -> SSOProviderType:
        return SSOProviderType.GITHUB

    async def get_authorization_url(self, state: str) -> str:
        import urllib.parse
        params = {
            "client_id": self.config.client_id,
            "redirect_uri": self.config.redirect_uri,
            "scope": " ".join(self.config.scopes),
            "state": state,
        }
        return f"https://github.com/login/oauth/authorize?{urllib.parse.urlencode(params)}"

    async def handle_callback(self, code: str, state: str) -> SSOUserInfo:
        import httpx

        async with httpx.AsyncClient() as client:
            token_response = await client.post(
                "https://github.com/login/oauth/access_token",
                json={
                    "client_id": self.config.client_id,
                    "client_secret": self.config.client_secret,
                    "code": code,
                },
                headers={"Accept": "application/json"},
            )
            token_data = token_response.json()
            access_token = token_data.get("access_token")

            user_response = await client.get(
                "https://api.github.com/user",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            user_data = user_response.json()

            email_response = await client.get(
                "https://api.github.com/user/emails",
                headers={"Authorization": f"Bearer {access_token}"},
            )
            emails = email_response.json()
            primary_email = next((e["email"] for e in emails if e.get("primary")), "")

        return SSOUserInfo(
            subject=str(user_data.get("id", "")),
            email=primary_email,
            name=user_data.get("name"),
            given_name=user_data.get("login"),
            picture=user_data.get("avatar_url"),
            attributes=user_data,
        )

    async def validate_token(self, token: str) -> SSOUserInfo | None:
        return None


class SSOManager:
    """Manages SSO provider configurations and authentication."""

    def __init__(self):
        self._providers: dict[str, BaseSSOProvider] = {}
        self._configs: dict[str, SSOConfig] = {}

    def register_provider(self, name: str, provider: BaseSSOProvider) -> None:
        self._providers[name] = provider
        self._configs[name] = provider.config

    def get_provider(self, name: str) -> BaseSSOProvider | None:
        return self._providers.get(name)

    def list_providers(self) -> list[dict[str, Any]]:
        return [
            {
                "name": name,
                "type": config.provider_type.value,
                "enabled": config.enabled,
            }
            for name, config in self._configs.items()
        ]

    async def get_authorization_url(self, provider_name: str, state: str) -> str:
        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(f"SSO provider not found: {provider_name}")
        return await provider.get_authorization_url(state)

    async def handle_callback(self, provider_name: str, code: str, state: str) -> SSOUserInfo:
        provider = self._providers.get(provider_name)
        if not provider:
            raise ValueError(f"SSO provider not found: {provider_name}")
        return await provider.handle_callback(code, state)

    async def validate_token(self, provider_name: str, token: str) -> SSOUserInfo | None:
        provider = self._providers.get(provider_name)
        if not provider:
            return None
        return await provider.validate_token(token)


sso_manager = SSOManager()
