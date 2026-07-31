"""
Identity Engine
"""

import uuid
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any


@dataclass
class Identity:
    id: str
    name: str
    email: str
    identity_type: str = "user"
    organization_id: str = ""
    attributes: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
    created_at: datetime = field(default_factory=datetime.now)


class IdentityEngine:
    def __init__(self):
        self.identities: dict[str, Identity] = {}
        self.listeners = []

    def create_identity(self, name: str, email: str, identity_type: str = "user", **kwargs) -> Identity:
        identity = Identity(id=str(uuid.uuid4()), name=name, email=email, identity_type=identity_type, **kwargs)
        self.identities[identity.id] = identity
        return identity

    def get_identity(self, identity_id: str) -> Identity | None:
        return self.identities.get(identity_id)

    def update_identity(self, identity_id: str, **kwargs) -> bool:
        identity = self.get_identity(identity_id)
        if identity:
            for k, v in kwargs.items():
                if hasattr(identity, k):
                    setattr(identity, k, v)
            return True
        return False

    def delete_identity(self, identity_id: str) -> bool:
        if identity_id in self.identities:
            del self.identities[identity_id]
            return True
        return False

    def list_identities(self) -> list[Identity]:
        return list(self.identities.values())

    def find_by_email(self, email: str) -> Identity | None:
        for identity in self.identities.values():
            if identity.email == email:
                return identity
        return None

    def find_by_organization(self, org_id: str) -> list[Identity]:
        return [i for i in self.identities.values() if i.organization_id == org_id]

    def count(self) -> int:
        return len(self.identities)
