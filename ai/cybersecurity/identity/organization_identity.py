"""
Organization Identity
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class OrganizationIdentity:
    org_id: str
    name: str
    domain: str = ""
    industry: str = ""
    size: str = ""
    logo_url: str = ""
    settings: dict[str, Any] = field(default_factory=dict)
    security_level: str = "medium"
    compliance_requirements: list[str] = field(default_factory=list)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class OrganizationManager:
    def __init__(self):
        self.organizations: dict[str, OrganizationIdentity] = {}

    def create_organization(self, org_id: str, name: str, **kwargs) -> OrganizationIdentity:
        org = OrganizationIdentity(org_id=org_id, name=name, **kwargs)
        self.organizations[org_id] = org
        return org

    def get_organization(self, org_id: str) -> OrganizationIdentity | None:
        return self.organizations.get(org_id)

    def update_organization(self, org_id: str, **kwargs) -> bool:
        org = self.get_organization(org_id)
        if org:
            for k, v in kwargs.items():
                if hasattr(org, k):
                    setattr(org, k, v)
            return True
        return False

    def delete_organization(self, org_id: str) -> bool:
        if org_id in self.organizations:
            del self.organizations[org_id]
            return True
        return False

    def find_by_domain(self, domain: str) -> OrganizationIdentity | None:
        for org in self.organizations.values():
            if org.domain == domain:
                return org
        return None

    def list_active(self) -> list[OrganizationIdentity]:
        return [o for o in self.organizations.values() if o.is_active]

    def count(self) -> int:
        return len(self.organizations)
