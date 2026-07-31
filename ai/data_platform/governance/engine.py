"""Governance engine."""
import uuid
from datetime import datetime
from typing import Dict, List, Optional
from .models import AccessPolicy, RetentionPolicy, AuditEntry, ComplianceRule
from .models import AccessLevel, ComplianceStandard, PolicyStatus


class GovernanceEngine:
    def __init__(self):
        self._access_policies: Dict[str, AccessPolicy] = {}
        self._retention_policies: Dict[str, RetentionPolicy] = {}
        self._audit_log: List[AuditEntry] = []
        self._compliance_rules: Dict[str, ComplianceRule] = {}

    def set_access(self, policy: AccessPolicy) -> AccessPolicy:
        self._access_policies[policy.policy_id] = policy
        return policy

    def check_access(self, user_id: str, dataset: str, required_level: AccessLevel = AccessLevel.READ) -> bool:
        hierarchy = {AccessLevel.NONE: 0, AccessLevel.READ: 1, AccessLevel.WRITE: 2, AccessLevel.ADMIN: 3}
        for p in self._access_policies.values():
            if p.user_id == user_id and p.dataset == dataset:
                if p.expires_at and p.expires_at < datetime.now():
                    continue
                if hierarchy.get(p.access_level, 0) >= hierarchy.get(required_level, 0):
                    return True
        return False

    def get_user_access(self, user_id: str) -> List[AccessPolicy]:
        return [p for p in self._access_policies.values() if p.user_id == user_id]

    def set_retention(self, policy: RetentionPolicy) -> RetentionPolicy:
        self._retention_policies[policy.policy_id] = policy
        return policy

    def get_retention(self, dataset: str) -> Optional[RetentionPolicy]:
        for p in self._retention_policies.values():
            if p.dataset == dataset:
                return p
        return None

    def log_access(self, entry: AuditEntry) -> AuditEntry:
        self._audit_log.append(entry)
        return entry

    def get_audit_log(self, user_id: Optional[str] = None, dataset: Optional[str] = None) -> List[AuditEntry]:
        log = list(self._audit_log)
        if user_id:
            log = [e for e in log if e.user_id == user_id]
        if dataset:
            log = [e for e in log if e.dataset == dataset]
        return log

    def add_compliance_rule(self, rule: ComplianceRule) -> ComplianceRule:
        self._compliance_rules[rule.rule_id] = rule
        return rule

    def get_compliance_rules(self, standard: Optional[ComplianceStandard] = None) -> List[ComplianceRule]:
        rules = list(self._compliance_rules.values())
        if standard:
            rules = [r for r in rules if r.standard == standard]
        return rules

    def get_stats(self) -> dict:
        return {
            "access_policies": len(self._access_policies),
            "retention_policies": len(self._retention_policies),
            "audit_entries": len(self._audit_log),
            "compliance_rules": len(self._compliance_rules),
        }
