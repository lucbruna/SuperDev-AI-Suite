from __future__ import annotations as __

import asyncio
import xml.etree.ElementTree as ET
from datetime import datetime
from typing import Dict, Any, Optional
from uuid import uuid4

from pydantic import BaseModel


class SAMLResponse(BaseModel):
    assertion_xml: str
    issuer: str
    name_id: str
    attributes: Dict[str, Any]
    session_index: str = ""
    not_on_or_after: datetime | None = None


class UserInfo(BaseModel):
    id: str
    email: str
    name: str
    provider: str = "saml"
    groups: list[str] = []


class SAMLProvider:
    def __init__(
        self,
        entity_id: str = "",
        sso_url: str = "",
        certificate: str = "",
        **kwargs: Any,
    ) -> None:
        self.entity_id = entity_id or f"https://saml.{uuid4().hex[:8]}.com"
        self.sso_url = sso_url or f"https://login.{uuid4().hex[:8]}.com/saml"
        self.certificate = certificate or ""

    async def get_auth_url(self) -> str:
        await asyncio.sleep(0.01)
        import urllib.parse

        params = urllib.parse.urlencode({
            "SAMLRequest": "mock_request",
            "RelayState": self.entity_id,
        })
        return f"{self.sso_url}?{params}"

    async def handle_callback(self, response: Dict[str, Any]) -> UserInfo:
        await asyncio.sleep(0.02)
        raw_xml = response.get("SAMLResponse", "")
        if not raw_xml:
            raise ValueError("Missing SAMLResponse")

        try:
            root = ET.fromstring(raw_xml)
            ns = {"saml": "urn:oasis:names:tc:SAML:2.0:assertion"}
            name_id_el = root.find(".//saml:NameID", ns)
            name_id = name_id_el.text if name_id_el is not None else "unknown"
        except ET.ParseError:
            name_id = f"user_{uuid4().hex[:8]}"

        return UserInfo(
            id=name_id,
            email=f"{name_id}@saml.example.com",
            name=name_id.replace(".", " ").title(),
            provider="saml",
            groups=[],
        )

    async def get_user_info(self, assertion: str) -> UserInfo:
        await asyncio.sleep(0.01)
        return await self.handle_callback({"SAMLResponse": assertion})

    def parse_assertion(self, raw_xml: str) -> SAMLResponse:
        root = ET.fromstring(raw_xml)
        ns = {
            "saml": "urn:oasis:names:tc:SAML:2.0:assertion",
            "samlp": "urn:oasis:names:tc:SAML:2.0:protocol",
        }
        name_id = root.findtext(".//saml:NameID", default="", namespaces=ns)
        issuer = root.findtext(".//saml:Issuer", default="", namespaces=ns)

        attributes: Dict[str, Any] = {}
        for attr in root.findall(".//saml:Attribute", ns):
            name = attr.get("Name", "")
            vals = [
                v.text for v in attr.findall("saml:AttributeValue", ns) if v.text
            ]
            if vals:
                attributes[name] = vals[0] if len(vals) == 1 else vals

        return SAMLResponse(
            assertion_xml=raw_xml,
            issuer=issuer,
            name_id=name_id,
            attributes=attributes,
        )
