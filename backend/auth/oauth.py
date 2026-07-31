from abc import ABC, abstractmethod
from typing import Any

import httpx


class OAuthHandler(ABC):
    def __init__(
        self,
        client_id: str,
        client_secret: str,
        redirect_uri: str,
        authorize_url: str,
        token_url: str,
        user_info_url: str,
        scope: str = "openid email profile",
    ) -> None:
        self.client_id = client_id
        self.client_secret = client_secret
        self.redirect_uri = redirect_uri
        self.authorize_url = authorize_url
        self.token_url = token_url
        self.user_info_url = user_info_url
        self.scope = scope

    @abstractmethod
    def authorize(self, state: str) -> str: ...

    @abstractmethod
    async def callback(self, code: str, state: str) -> dict[str, Any]: ...

    @abstractmethod
    async def get_user_info(self, access_token: str) -> dict[str, Any]: ...


class GoogleOAuthHandler(OAuthHandler):
    def authorize(self, state: str) -> str:
        params = (
            f"client_id={self.client_id}"
            f"&redirect_uri={self.redirect_uri}"
            f"&scope={self.scope}"
            f"&state={state}"
            f"&response_type=code"
            f"&access_type=offline"
        )
        return f"{self.authorize_url}?{params}"

    async def callback(self, code: str, state: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                self.token_url,
                data={
                    "code": code,
                    "client_id": self.client_id,
                    "client_secret": self.client_secret,
                    "redirect_uri": self.redirect_uri,
                    "grant_type": "authorization_code",
                },
                headers={"Accept": "application/json"},
            )
            response.raise_for_status()
            return response.json()

    async def get_user_info(self, access_token: str) -> dict[str, Any]:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                self.user_info_url,
                headers={"Authorization": f"Bearer {access_token}"},
            )
            response.raise_for_status()
            return response.json()
