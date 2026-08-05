"""ModuleVersion: deterministic semantic version parsing and constraint checks."""
from __future__ import annotations

import re

_VERSION_RE = re.compile(
    r"^(?P<op>==|!=|>=|<=|>|<|~=)?\s*"
    r"(?P<ver>[0-9]+(?:\.[0-9]+){0,2}(?:[-+][\w.\-]+)?)$"
)


class ModuleVersion:
    def __init__(self, version: str) -> None:
        self.raw = str(version).strip()
        core, _, pre = self.raw.partition("-")
        parts = core.split(".")
        self.major = int(parts[0]) if parts and parts[0].isdigit() else 0
        self.minor = int(parts[1]) if len(parts) > 1 and parts[1].isdigit() else 0
        self.patch = int(parts[2]) if len(parts) > 2 and parts[2].isdigit() else 0
        self.prerelease: str | None = pre or None
        self.parts = (self.major, self.minor, self.patch)

    def _key(self) -> tuple:
        return (
            self.major,
            self.minor,
            self.patch,
            0 if self.prerelease is None else 1,
            self.prerelease or "",
        )

    def __eq__(self, other: object) -> bool:
        return isinstance(other, ModuleVersion) and self._key() == other._key()

    def __lt__(self, other: object) -> bool:
        return isinstance(other, ModuleVersion) and self._key() < other._key()

    def __le__(self, other: object) -> bool:
        return isinstance(other, ModuleVersion) and self._key() <= other._key()

    def __gt__(self, other: object) -> bool:
        return isinstance(other, ModuleVersion) and self._key() > other._key()

    def __ge__(self, other: object) -> bool:
        return isinstance(other, ModuleVersion) and self._key() >= other._key()

    def __hash__(self) -> int:
        return hash(self._key())

    def __str__(self) -> str:
        return self.raw

    @staticmethod
    def satisfies(version: "ModuleVersion", constraint: str) -> bool:
        """Check ``version`` against a constraint such as ``>=1.0``, ``~=1.4``."""
        constraint = (constraint or "").strip()
        if not constraint:
            return True
        match = _VERSION_RE.match(constraint)
        if not match:
            return True
        op = match.group("op") or "=="
        other = ModuleVersion(match.group("ver"))
        if op == "==":
            return version == other
        if op == "!=":
            return version != other
        if op == ">":
            return version > other
        if op == ">=":
            return version >= other
        if op == "<":
            return version < other
        if op == "<=":
            return version <= other
        if op == "~=":
            if len(other.parts) < 2:
                return version >= other
            upper = ModuleVersion(f"{other.parts[0]}.{other.parts[1] + 1}.0")
            return version >= other and version < upper
        return True
