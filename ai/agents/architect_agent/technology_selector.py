from __future__ import annotations

from typing import Any

DEFAULT_TECHNOLOGIES: list[dict[str, Any]] = [
    {
        "name": "Python",
        "category": "language",
        "use_cases": ["backend", "data", "ml", "automation", "api"],
        "pros": ["readable", "large ecosystem", "cross-platform"],
        "cons": ["performance", "GIL"],
    },
    {
        "name": "TypeScript",
        "category": "language",
        "use_cases": ["frontend", "backend", "fullstack", "api"],
        "pros": ["type safety", "ecosystem", "versatile"],
        "cons": ["build step", "complexity"],
    },
    {
        "name": "PostgreSQL",
        "category": "database",
        "use_cases": ["relational", "analytics", "geospatial", "oltp"],
        "pros": ["reliable", "feature-rich", "open-source"],
        "cons": ["vertical scaling limits"],
    },
    {
        "name": "Redis",
        "category": "cache",
        "use_cases": ["caching", "session", "pub-sub", "rate-limiting"],
        "pros": ["fast", "simple", "proven"],
        "cons": ["in-memory", "no complex queries"],
    },
    {
        "name": "React",
        "category": "frontend",
        "use_cases": ["spa", "dashboard", "web-app", "mobile-web"],
        "pros": ["component model", "eco-system", "performance"],
        "cons": ["tooling churn", "bundle size"],
    },
    {
        "name": "FastAPI",
        "category": "framework",
        "use_cases": ["rest-api", "microservice", "async-web"],
        "pros": ["performance", "auto-docs", "pydantic"],
        "cons": ["newer", "smaller community"],
    },
    {
        "name": "Docker",
        "category": "infrastructure",
        "use_cases": ["containerization", "deployment", "dev-environment"],
        "pros": ["portable", "consistent", "ecosystem"],
        "cons": ["learning curve", "overhead"],
    },
]


class TechnologySelector:
    """Recommends technology choices based on requirements."""

    def __init__(self) -> None:
        self._catalog: dict[str, dict[str, Any]] = {t["name"]: dict(t) for t in DEFAULT_TECHNOLOGIES}

    def recommend(self, requirements: list[str]) -> list[dict[str, Any]]:
        req_lower = [r.lower() for r in requirements]
        results: list[dict[str, Any]] = []
        for tech in self._catalog.values():
            score = sum(1 for use in tech["use_cases"] if any(use in req for req in req_lower))
            if score > 0:
                results.append(
                    {
                        "name": tech["name"],
                        "category": tech["category"],
                        "score": score,
                        "pros": tech["pros"],
                        "cons": tech["cons"],
                    }
                )
        results.sort(key=lambda x: x["score"], reverse=True)
        return results

    def add_technology(
        self,
        name: str,
        category: str,
        use_cases: list[str],
    ) -> str:
        self._catalog[name] = {
            "name": name,
            "category": category,
            "use_cases": use_cases,
            "pros": [],
            "cons": [],
        }
        return name

    def get_technology(self, name: str) -> dict[str, Any] | None:
        return self._catalog.get(name)

    def list_by_category(self, category: str) -> list[dict[str, Any]]:
        return [dict(t) for t in self._catalog.values() if t["category"] == category]

    def to_dict(self) -> dict[str, Any]:
        return {
            "technologies": list(self._catalog.values()),
            "category_count": len({t["category"] for t in self._catalog.values()}),
        }
