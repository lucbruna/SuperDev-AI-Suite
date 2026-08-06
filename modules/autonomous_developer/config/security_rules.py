"""Security rules — path and secret guardrails for autonomous changes.

Environment prefix: ``SUPERDEV_AD_SECURITY_*``.
"""
from __future__ import annotations

import os
import re
from dataclasses import dataclass, field
from pathlib import Path


def _env_bool(key: str, default: bool) -> bool:
    raw = os.getenv(key)
    if raw is None:
        return default
    return raw.strip().lower() in {"1", "true", "yes", "on"}


# A bare secret keyword anywhere in the text marks it as secret-like.
_SECRET_KEYWORD = re.compile(
    r"(?i)(api[_-]?key|secret|password|passwd|token|private[_-]?key)"
)

# High-signal value patterns: the secret itself, not just its name.
_SECRET_VALUE_PATTERNS: tuple[re.Pattern[str], ...] = (
    re.compile(r"(?i)Bearer\s+[A-Za-z0-9._~+/-]+=?"),
    re.compile(r"\bAKIA[0-9A-Z]{16}\b"),  # AWS access key id
    re.compile(r"(?i)ghp_[A-Za-z0-9]{36}"),  # GitHub PAT
    re.compile(r"-----BEGIN (RSA |EC |OPENSSH )?PRIVATE KEY-----"),
)

# Keyword followed by a value: key=value / key: value / key value.
_SECRET_ASSIGNMENT = re.compile(
    r"(?i)(api[_-]?key|secret|password|passwd|token|private[_-]?key)"
    r"(\s*[=:]\s*|\s+)[\"']?[A-Za-z0-9._~+/\\-]{4,}"
)


@dataclass(slots=True)
class SecurityRules:
    """Guardrails constraining what the developer may do."""

    allow_shell_execution: bool = False
    allow_network_access: bool = False
    allow_secret_writes: bool = False

    # Paths the developer may touch. Empty tuple == project root only.
    allowed_paths: tuple[str, ...] = field(default_factory=tuple)
    # Glob patterns never touched regardless of allowed_paths.
    blocked_patterns: tuple[str, ...] = field(
        default_factory=lambda: (".env", ".env.*", "*.pem", "*.key", ".superdev", "node_modules")
    )

    redact_secrets_in_logs: bool = True
    forbid_subprocess_with_shell: bool = True
    require_command_allowlist: bool = True
    max_command_timeout_seconds: int = 300

    @classmethod
    def from_env(cls) -> SecurityRules:
        cfg = cls()
        cfg.allow_shell_execution = _env_bool(
            "SUPERDEV_AD_SECURITY_SHELL", cfg.allow_shell_execution
        )
        cfg.allow_network_access = _env_bool(
            "SUPERDEV_AD_SECURITY_NETWORK", cfg.allow_network_access
        )
        cfg.allow_secret_writes = _env_bool(
            "SUPERDEV_AD_SECURITY_SECRETS", cfg.allow_secret_writes
        )
        raw = os.getenv("SUPERDEV_AD_SECURITY_ALLOWED_PATHS")
        if raw:
            cfg.allowed_paths = tuple(p.strip() for p in raw.split(";") if p.strip())
        return cfg

    def is_path_allowed(self, path: str | Path, project_root: str | Path | None = None) -> bool:
        """Return True if the developer may write to ``path``.

        Paths outside the project root (or the configured allowed roots) are
        rejected, as are paths matching a blocked pattern.
        """
        p = Path(path)
        if self.allowed_paths:
            for base in self.allowed_paths:
                base_p = Path(base)
                try:
                    p.resolve().relative_to(base_p.resolve())
                    return not self._matches_blocked(p)
                except ValueError:
                    continue
            return False
        if project_root is None:
            return False
        root = Path(project_root)
        try:
            p.resolve().relative_to(root.resolve())
        except ValueError:
            return False
        return not self._matches_blocked(p)

    def _matches_blocked(self, path: Path) -> bool:
        import fnmatch

        name = path.name
        rel = str(path)
        return any(
            fnmatch.fnmatch(name, pattern) or fnmatch.fnmatch(rel, pattern)
            for pattern in self.blocked_patterns
        )


def contains_secret(text: str) -> bool:
    """Return True if ``text`` looks like it carries a secret value."""
    return _SECRET_KEYWORD.search(text) is not None or any(
        pattern.search(text) for pattern in _SECRET_VALUE_PATTERNS
    )


def redact_secrets(text: str) -> str:
    """Replace secret-looking values with a placeholder for logs."""
    redacted = _SECRET_ASSIGNMENT.sub("[REDACTED]", text)
    for pattern in _SECRET_VALUE_PATTERNS:
        redacted = pattern.sub("[REDACTED]", redacted)
    return redacted
