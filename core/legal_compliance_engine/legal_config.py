"""
Legal Configuration - Global legal AI engine configuration.
"""

from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


@dataclass
class ContractsConfig:
    auto_review: bool = True
    min_risk_threshold: float = 30.0
    enable_clause_detection: bool = True
    enable_obligation_tracking: bool = True
    auto_generate_standard: bool = True
    max_review_hours: float = 48.0


@dataclass
class DocumentsConfig:
    auto_classify: bool = True
    enable_search: bool = True
    enable_summary: bool = True
    retention_default_years: int = 5
    archive_after_months: int = 36
    supported_formats: List[str] = field(default_factory=lambda: ["pdf", "docx", "txt"])


@dataclass
class RegulationsConfig:
    monitor_enabled: bool = True
    check_interval_hours: int = 24
    jurisdictions: List[str] = field(default_factory=lambda: ["brazil", "usa", "eu"])
    auto_assess_impact: bool = True
    alert_on_change: bool = True


@dataclass
class ComplianceConfig:
    auto_check: bool = True
    check_frequency_days: int = 7
    violation_escalation: bool = True
    control_testing_enabled: bool = True
    max_violations_before_alert: int = 3


@dataclass
class LegalRiskConfig:
    enable_assessment: bool = True
    assessment_frequency_days: int = 30
    risk_score_threshold_high: float = 60.0
    risk_score_threshold_critical: float = 80.0
    financial_exposure_limit: float = 1000000.0


@dataclass
class LegalAuditConfig:
    enable_auto_audit: bool = True
    audit_frequency_days: int = 90
    evidence_collection_enabled: bool = True
    max_findings_per_audit: int = 50


@dataclass
class PoliciesConfig:
    enable_auto_create: bool = True
    require_acknowledgment: bool = True
    review_frequency_days: int = 365
    acknowledgment_grace_days: int = 30


@dataclass
class LitigationConfig:
    enable_deadline_tracking: bool = True
    deadline_reminder_days: int = 7
    enable_predictions: bool = True
    prediction_confidence_min: float = 0.6


@dataclass
class SecurityConfig:
    enable_encryption: bool = True
    enable_access_control: bool = True
    audit_trail_enabled: bool = True
    sensitive_fields: List[str] = field(default_factory=lambda: ["contract_value", "tax_id", "legal_opinion", "evidence"])
    session_timeout_minutes: int = 30


@dataclass
class IntegrationConfig:
    enable_erp_sync: bool = True
    enable_finance_sync: bool = True
    enable_crm_sync: bool = True
    finance_sync_interval_minutes: int = 60
    decision_center_enabled: bool = True


@dataclass
class LegalConfig:
    engine_name: str = "LegalAIEngine"
    engine_version: str = "1.0.0"
    environment: str = "production"
    log_level: str = "INFO"
    enable_telemetry: bool = True
    contracts: ContractsConfig = field(default_factory=ContractsConfig)
    documents: DocumentsConfig = field(default_factory=DocumentsConfig)
    regulations: RegulationsConfig = field(default_factory=RegulationsConfig)
    compliance: ComplianceConfig = field(default_factory=ComplianceConfig)
    risk: LegalRiskConfig = field(default_factory=LegalRiskConfig)
    audit: LegalAuditConfig = field(default_factory=LegalAuditConfig)
    policies: PoliciesConfig = field(default_factory=PoliciesConfig)
    litigation: LitigationConfig = field(default_factory=LitigationConfig)
    security: SecurityConfig = field(default_factory=SecurityConfig)
    integrations: IntegrationConfig = field(default_factory=IntegrationConfig)
    enable_legal_digital_twin: bool = True
    enable_autonomous_compliance: bool = True
    enable_continuous_learning: bool = True
    _extra: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "LegalConfig":
        config = cls()
        for key, value in data.items():
            if hasattr(config, key) and not key.startswith("_"):
                if isinstance(value, dict) and key in cls.__dataclass_fields__:
                    sub = getattr(config, key)
                    if hasattr(sub, "__dataclass_fields__"):
                        for sk, sv in value.items():
                            if hasattr(sub, sk):
                                setattr(sub, sk, sv)
                        continue
                setattr(config, key, value)
            else:
                config._extra[key] = value
        return config

    @classmethod
    def from_json(cls, path: str) -> "LegalConfig":
        if not os.path.exists(path):
            return cls()
        with open(path) as f:
            return cls.from_dict(json.load(f))

    def to_dict(self) -> Dict[str, Any]:
        return asdict(self)

    def to_json(self, path: str) -> None:
        with open(path, "w") as f:
            json.dump(self.to_dict(), f, indent=2, default=str)

    def validate(self) -> List[str]:
        errors = []
        if self.contracts.min_risk_threshold < 0 or self.contracts.min_risk_threshold > 100:
            errors.append("min_risk_threshold must be between 0 and 100")
        if self.risk.risk_score_threshold_high < 0:
            errors.append("risk_score_threshold_high must be positive")
        if self.litigation.deadline_reminder_days < 1:
            errors.append("deadline_reminder_days must be >= 1")
        return errors
