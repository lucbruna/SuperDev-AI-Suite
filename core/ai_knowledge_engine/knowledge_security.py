from __future__ import annotations

import hashlib
import logging
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional, Set

from .knowledge_config import KnowledgeConfig

logger = logging.getLogger(__name__)


class KnowledgeClassification(Enum):
    PUBLIC = "public"
    INTERNAL = "internal"
    CONFIDENTIAL = "confidential"
    RESTRICTED = "restricted"


class AccessAction(Enum):
    READ = "read"
    WRITE = "write"
    VALIDATE = "validate"
    DEPRECATE = "deprecate"
    ADMIN = "admin"


@dataclass
class AuditEntry:
    id: str
    user_id: str
    action: str
    resource_id: str
    resource_type: str
    details: str = ""
    timestamp: datetime = field(default_factory=datetime.utcnow)
    classification: str = "internal"


@dataclass
class ApprovalRequest:
    id: str
    request_type: str
    requester: str
    resource_id: str
    reason: str
    status: str = "pending"
    reviewers: List[str] = field(default_factory=list)
    approvals: List[str] = field(default_factory=list)
    rejections: List[str] = field(default_factory=list)
    created_at: datetime = field(default_factory=datetime.utcnow)
    resolved_at: Optional[datetime] = None


class AccessController:
    def __init__(self):
        self._roles: Dict[str, Set[str]] = {
            "admin": {"knowledge:read", "knowledge:write", "knowledge:validate",
                      "knowledge:deprecate", "knowledge:admin", "research:conduct",
                      "document:process", "graph:manage", "security:configure"},
            "researcher": {"knowledge:read", "knowledge:write", "research:conduct",
                           "document:process", "graph:read"},
            "analyst": {"knowledge:read", "knowledge:write", "document:process",
                        "research:conduct", "graph:read"},
            "viewer": {"knowledge:read", "graph:read", "research:read"},
            "auditor": {"knowledge:read", "security:audit", "graph:read"},
        }
        self._permissions: Dict[str, Dict[str, Any]] = {}
        self._domain_access: Dict[str, Set[str]] = {}

    def set_user_role(self, user_id: str, role: str) -> None:
        if role not in self._roles:
            raise ValueError(f"Invalid role: {role}")
        self._permissions[user_id] = {"role": role}

    def get_user_role(self, user_id: str) -> Optional[str]:
        entry = self._permissions.get(user_id)
        return entry.get("role") if entry else None

    def grant_domain_access(self, user_id: str, domain: str) -> None:
        if user_id not in self._domain_access:
            self._domain_access[user_id] = set()
        self._domain_access[user_id].add(domain)

    def revoke_domain_access(self, user_id: str, domain: str) -> None:
        if user_id in self._domain_access:
            self._domain_access[user_id].discard(domain)

    def check_access(self, user_id: str, resource: str, action: str) -> bool:
        entry = self._permissions.get(user_id)
        if not entry:
            return False
        role = entry.get("role", "")
        required = f"{resource}:{action}"
        return required in self._roles.get(role, set())

    def check_domain_access(self, user_id: str, domain: str) -> bool:
        entry = self._permissions.get(user_id)
        if not entry:
            return False
        role = entry.get("role", "")
        if role == "admin":
            return True
        domains = self._domain_access.get(user_id, set())
        return domain in domains

    def list_roles(self) -> List[str]:
        return list(self._roles.keys())

    def list_permissions_for_role(self, role: str) -> Set[str]:
        return self._roles.get(role, set())


class SourceValidator:
    def __init__(self):
        self._trusted_domains: Set[str] = set()
        self._blocked_domains: Set[str] = set()
        self._source_reliability: Dict[str, float] = {}

    def add_trusted_domain(self, domain: str) -> None:
        self._trusted_domains.add(domain)

    def add_blocked_domain(self, domain: str) -> None:
        self._blocked_domains.add(domain)

    def set_source_reliability(self, source_id: str, score: float) -> None:
        self._source_reliability[source_id] = max(0.0, min(1.0, score))

    def validate_source(self, source: Any) -> Dict[str, Any]:
        issues = []
        score = 0.5
        if hasattr(source, "url") and source.url:
            for domain in self._blocked_domains:
                if domain in source.url:
                    issues.append(f"Source from blocked domain: {domain}")
                    score = 0.0
            for domain in self._trusted_domains:
                if domain in source.url:
                    score = max(score, 0.9)
        if hasattr(source, "id") and source.id in self._source_reliability:
            score = self._source_reliability[source.id]
        if hasattr(source, "reliability_score"):
            score = (score + source.reliability_score) / 2
        return {"valid": len(issues) == 0, "score": score, "issues": issues}

    def get_reliability(self, source_id: str) -> float:
        return self._source_reliability.get(source_id, 0.5)


class KnowledgeClassifier:
    def __init__(self):
        self._classification_rules: Dict[str, List[str]] = {
            "public": [],
            "internal": [],
            "confidential": ["financial", "personnel", "strategy"],
            "restricted": ["security", "credentials", "legal_privilege"],
        }

    def classify(self, content: str, domain: str = "general",
                 tags: Optional[List[str]] = None) -> KnowledgeClassification:
        tags = tags or []
        content_lower = content.lower()
        for keyword in self._classification_rules["restricted"]:
            if keyword in content_lower or keyword in tags:
                return KnowledgeClassification.RESTRICTED
        for keyword in self._classification_rules["confidential"]:
            if keyword in content_lower or keyword in tags or keyword in domain:
                return KnowledgeClassification.CONFIDENTIAL
        if domain == "general" and not tags:
            return KnowledgeClassification.PUBLIC
        return KnowledgeClassification.INTERNAL

    def add_rule(self, classification: str, keyword: str) -> None:
        if classification in self._classification_rules:
            self._classification_rules[classification].append(keyword)


class AuditTrail:
    def __init__(self, max_entries: int = 10000):
        self._entries: List[AuditEntry] = []
        self._max_entries = max_entries

    def record(self, user_id: str, action: str, resource_id: str,
               resource_type: str, details: str = "",
               classification: str = "internal") -> AuditEntry:
        entry = AuditEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            action=action,
            resource_id=resource_id,
            resource_type=resource_type,
            details=details,
            classification=classification,
        )
        self._entries.append(entry)
        if len(self._entries) > self._max_entries:
            self._entries = self._entries[-self._max_entries // 2:]
        return entry

    def query(self, resource_id: Optional[str] = None, user_id: Optional[str] = None,
              action: Optional[str] = None, limit: int = 100) -> List[AuditEntry]:
        results = self._entries
        if resource_id:
            results = [e for e in results if e.resource_id == resource_id]
        if user_id:
            results = [e for e in results if e.user_id == user_id]
        if action:
            results = [e for e in results if e.action == action]
        return results[-limit:]

    def get_all(self, limit: int = 100) -> List[AuditEntry]:
        return self._entries[-limit:]

    def count(self) -> int:
        return len(self._entries)


class ApprovalManager:
    def __init__(self):
        self._requests: Dict[str, ApprovalRequest] = {}

    def create_request(self, request_type: str, requester: str,
                       resource_id: str, reason: str,
                       reviewers: Optional[List[str]] = None) -> ApprovalRequest:
        req = ApprovalRequest(
            id=str(uuid.uuid4()),
            request_type=request_type,
            requester=requester,
            resource_id=resource_id,
            reason=reason,
            reviewers=reviewers or [],
        )
        self._requests[req.id] = req
        return req

    def approve(self, request_id: str, reviewer: str) -> bool:
        req = self._requests.get(request_id)
        if not req or req.status != "pending":
            return False
        if reviewer not in req.reviewers:
            return False
        if reviewer not in req.approvals:
            req.approvals.append(reviewer)
        if len(req.approvals) >= len(req.reviewers):
            req.status = "approved"
            req.resolved_at = datetime.utcnow()
        return True

    def reject(self, request_id: str, reviewer: str) -> bool:
        req = self._requests.get(request_id)
        if not req or req.status != "pending":
            return False
        if reviewer not in req.reviewers:
            return False
        if reviewer not in req.rejections:
            req.rejections.append(reviewer)
        req.status = "rejected"
        req.resolved_at = datetime.utcnow()
        return True

    def get_request(self, request_id: str) -> Optional[ApprovalRequest]:
        return self._requests.get(request_id)

    def get_pending(self) -> List[ApprovalRequest]:
        return [r for r in self._requests.values() if r.status == "pending"]

    def get_for_user(self, user_id: str) -> List[ApprovalRequest]:
        return [r for r in self._requests.values()
                if user_id in r.reviewers or r.requester == user_id]


class KnowledgeSecurityManager:
    def __init__(self, config: Optional[KnowledgeConfig] = None):
        self._config = config or KnowledgeConfig()
        self.access = AccessController()
        self.source_validator = SourceValidator()
        self.classifier = KnowledgeClassifier()
        self.audit = AuditTrail()
        self.approvals = ApprovalManager()

    def verify_access(self, user_id: str, resource: str, action: str) -> bool:
        allowed = self.access.check_access(user_id, resource, action)
        self.audit.record(user_id, f"access_{action}", resource,
                          "knowledge", f"Access {'granted' if allowed else 'denied'}")
        return allowed

    def verify_domain_access(self, user_id: str, domain: str) -> bool:
        return self.access.check_domain_access(user_id, domain)

    def classify_knowledge(self, content: str, domain: str = "general",
                           tags: Optional[List[str]] = None) -> KnowledgeClassification:
        return self.classifier.classify(content, domain, tags)

    def validate_source(self, source: Any) -> Dict[str, Any]:
        return self.source_validator.validate_source(source)

    def get_security_report(self) -> Dict[str, Any]:
        return {
            "roles": self.access.list_roles(),
            "audit_count": self.audit.count(),
            "pending_approvals": len(self.approvals.get_pending()),
            "trusted_domains": list(getattr(self.source_validator, "_trusted_domains", set())),
            "classification_rules": {k: len(v) for k, v in self.classifier._classification_rules.items()},
        }