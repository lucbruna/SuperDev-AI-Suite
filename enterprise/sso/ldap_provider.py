from __future__ import annotations as __

import asyncio
from typing import Dict, Any, List, Optional
from uuid import uuid4

from pydantic import BaseModel


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    provider: str = "ldap"
    groups: list[str] = []
    dn: str = ""


class LDAPProvider:
    def __init__(
        self,
        server_url: str = "",
        base_dn: str = "",
        bind_dn: str = "",
        bind_password: str = "",
        user_search_base: str = "",
        group_search_base: str = "",
        **kwargs: Any,
    ) -> None:
        self.server_url = server_url or f"ldap://{uuid4().hex[:8]}.example.com:389"
        self.base_dn = base_dn or "dc=example,dc=com"
        self.bind_dn = bind_dn or f"cn=admin,{self.base_dn}"
        self.bind_password = bind_password or ""
        self.user_search_base = user_search_base or f"ou=users,{self.base_dn}"
        self.group_search_base = group_search_base or f"ou=groups,{self.base_dn}"

    async def authenticate(
        self, username: str, password: str
    ) -> UserInfo:
        await asyncio.sleep(0.03)
        if not username or not password:
            raise ValueError("Username and password required")

        user_id = f"ldap_{username}"
        return UserInfo(
            id=user_id,
            email=f"{username}@ldap.example.com",
            name=username.replace(".", " ").title(),
            provider="ldap",
            groups=["users"],
            dn=f"uid={username},{self.user_search_base}",
        )

    async def search_users(self, filter_str: str = "") -> List[UserInfo]:
        await asyncio.sleep(0.02)
        return [
            UserInfo(
                id=f"ldap_user_{uuid4().hex[:6]}",
                email=f"user{i}@ldap.example.com",
                name=f"User {i}",
                provider="ldap",
                groups=["users"],
                dn=f"uid=user{i},{self.user_search_base}",
            )
            for i in range(3)
        ]

    async def get_groups(self, username: str) -> List[str]:
        await asyncio.sleep(0.01)
        return ["users", "developers"]

    async def check_group_membership(
        self, username: str, group: str
    ) -> bool:
        await asyncio.sleep(0.01)
        groups = await self.get_groups(username)
        return group in groups

    async def get_user_by_dn(self, dn: str) -> UserInfo | None:
        await asyncio.sleep(0.01)
        uid = dn.split("uid=")[1].split(",")[0] if "uid=" in dn else "unknown"
        return UserInfo(
            id=f"ldap_{uid}",
            email=f"{uid}@ldap.example.com",
            name=uid.title(),
            provider="ldap",
            groups=["users"],
            dn=dn,
        )
