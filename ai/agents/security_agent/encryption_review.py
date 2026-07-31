from __future__ import annotations

from typing import Any

WEAK_ALGORITHMS = {"md5", "sha1", "rc4", "des", "blowfish"}
STRONG_ALGORITHMS = {"aes-256", "aes-128", "sha256", "sha3-256", "sha512", "chacha20"}


class EncryptionReview:
    """Reviews encryption algorithms and configurations."""

    def __init__(self) -> None:
        self._standards: dict[str, dict[str, Any]] = {}

    def review_algorithm(self, algorithm: str, key_size: int) -> dict[str, Any]:
        algo_lower = algorithm.lower()
        if algo_lower in WEAK_ALGORITHMS:
            status = "non-compliant"
            risk = "high"
        elif algo_lower in STRONG_ALGORITHMS and key_size >= 128:
            status = "compliant"
            risk = "low"
        else:
            status = "needs-review"
            risk = "medium"
        return {
            "algorithm": algorithm,
            "key_size": key_size,
            "status": status,
            "risk": risk,
        }

    def add_standard(
        self,
        name: str,
        algorithm: str,
        key_size: int,
        status: str = "compliant",
    ) -> str:
        self._standards[name] = {
            "name": name,
            "algorithm": algorithm,
            "key_size": key_size,
            "status": status,
        }
        return name

    def get_standard(self, name: str) -> dict[str, Any] | None:
        return self._standards.get(name)

    def list_standards(self) -> list[dict[str, Any]]:
        return list(self._standards.values())

    @property
    def standard_count(self) -> int:
        return len(self._standards)

    def check_compliance(self, config: dict[str, Any]) -> list[dict[str, Any]]:
        results = []
        algo = config.get("algorithm", "unknown")
        key_size = config.get("key_size", 0)
        results.append(self.review_algorithm(algo, key_size))
        for std in self._standards.values():
            results.append(
                {
                    "standard": std["name"],
                    "required": std["algorithm"],
                    "configured": algo,
                    "compliant": algo.lower() == std["algorithm"].lower() and key_size >= std["key_size"],
                }
            )
        return results

    def to_dict(self) -> dict[str, Any]:
        return {
            "standards": list(self._standards.values()),
            "standard_count": self.standard_count,
        }
