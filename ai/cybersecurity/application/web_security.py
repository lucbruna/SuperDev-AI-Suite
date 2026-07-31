"""
Web Application Security - OWASP Top 10 Mitigations
"""
from typing import Dict, Any, Optional, List
from dataclasses import dataclass, field
from enum import Enum


class OWASPCategory(Enum):
    INJECTION = "A03:2021"
    BROKEN_AUTH = "A07:2021"
    SENSITIVE_DATA = "A02:2021"
    XXE = "A05:2021"
    BROKEN_ACCESS = "A01:2021"
    SECURITY_MISCONFIG = "A05:2021"
    XSS = "A03:2021"
    INSECURE_DESERIALIZATION = "A08:2021"
    VULN_COMPONENTS = "A06:2021"
    INSUFFICIENT_LOGGING = "A09:2021"


@dataclass
class SecurityHeader:
    name: str
    value: str
    required: bool = True
    description: str = ""


@dataclass
class ValidationResult:
    passed: bool
    category: str
    message: str = ""
    severity: str = "medium"
    recommendation: str = ""


class WebSecurity:
    def __init__(self):
        self.headers: List[SecurityHeader] = [
            SecurityHeader("X-Content-Type-Options", "nosniff"),
            SecurityHeader("X-Frame-Options", "DENY"),
            SecurityHeader("X-XSS-Protection", "1; mode=block"),
            SecurityHeader("Strict-Transport-Security", "max-age=31536000; includeSubDomains"),
            SecurityHeader("Content-Security-Policy", "default-src 'self'"),
            SecurityHeader("Referrer-Policy", "strict-origin-when-cross-origin"),
        ]
        self.blocked_patterns: List[str] = ["<script>", "javascript:", "onerror=", "onload="]

    def validate_input(self, input_str: str) -> ValidationResult:
        for pattern in self.blocked_patterns:
            if pattern.lower() in input_str.lower():
                return ValidationResult(passed=False, category="XSS", message=f"Blocked pattern: {pattern}", severity="high")
        return ValidationResult(passed=True, category="XSS", message="Input is safe")

    def get_security_headers(self) -> List[SecurityHeader]:
        return self.headers

    def add_header(self, name: str, value: str, required: bool = True) -> SecurityHeader:
        header = SecurityHeader(name=name, value=value, required=required)
        self.headers.append(header)
        return header

    def remove_header(self, name: str) -> bool:
        for i, h in enumerate(self.headers):
            if h.name == name:
                self.headers.pop(i)
                return True
        return False

    def validate_response_headers(self, headers: Dict[str, str]) -> List[ValidationResult]:
        results = []
        for h in self.headers:
            if h.required and h.name not in headers:
                results.append(ValidationResult(passed=False, category="Headers", message=f"Missing: {h.name}"))
            elif h.name in headers and headers[h.name] != h.value:
                results.append(ValidationResult(passed=False, category="Headers", message=f"Wrong value: {h.name}"))
        if not results:
            results.append(ValidationResult(passed=True, category="Headers", message="All headers valid"))
        return results

    def check_injection(self, input_str: str) -> ValidationResult:
        sql_patterns = ["'", "union select", "drop table", "insert into", "delete from"]
        for p in sql_patterns:
            if p in input_str.lower():
                return ValidationResult(passed=False, category="Injection", message=f"SQL injection pattern: {p}", severity="critical")
        return ValidationResult(passed=True, category="Injection", message="No injection detected")

    def sanitize_output(self, data: str) -> str:
        return data.replace("<", "&lt;").replace(">", "&gt;").replace('"', "&quot;").replace("'", "&#x27;")

    def count(self) -> int:
        return len(self.headers)
