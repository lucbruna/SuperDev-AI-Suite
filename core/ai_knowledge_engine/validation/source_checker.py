from __future__ import annotations

import asyncio
from datetime import datetime, timedelta
from typing import Any

DOMAIN_RELIABILITY: dict[str, float] = {
    "wikipedia.org": 0.85,
    "github.com": 0.80,
    "arxiv.org": 0.95,
    "nature.com": 0.98,
    "sciencedirect.com": 0.95,
    "ieee.org": 0.93,
    "acm.org": 0.92,
    "stackoverflow.com": 0.70,
    "medium.com": 0.50,
    "reddit.com": 0.30,
}


class SourceChecker:
    def __init__(self) -> None:
        self._cache: dict[str, dict[str, Any]] = {}

    async def check_source(self, url: str) -> dict[str, Any]:
        if url in self._cache:
            return self._cache[url]

        await asyncio.sleep(0.01)
        verification = await self.verify_url(url)
        reliability = await self.check_reliability(url)
        recency = await self.check_recency(url)
        relevance = await self.check_relevance(url)
        score = await self.get_source_score(url)

        result = {
            "url": url,
            "verified": verification["verified"],
            "reliability_score": reliability["score"],
            "is_recent": recency["is_recent"],
            "relevance_score": relevance["score"],
            "score": score,
            "details": {
                "verification": verification,
                "reliability": reliability,
                "recency": recency,
                "relevance": relevance,
            },
        }
        self._cache[url] = result
        return result

    async def verify_url(self, url: str) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        has_scheme = url.startswith(("http://", "https://"))
        has_domain = "." in url.split("://")[-1].split("/")[0] if "://" in url else "." in url
        is_valid_format = has_scheme and has_domain
        return {
            "verified": is_valid_format,
            "url": url,
            "has_scheme": has_scheme,
            "has_domain": has_domain,
        }

    async def check_reliability(self, url: str) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        domain = url.split("://")[-1].split("/")[0].lower()
        for known_domain, score in DOMAIN_RELIABILITY.items():
            if known_domain in domain:
                return {"score": score, "domain": known_domain, "source": "known"}
        base_domain = ".".join(domain.split(".")[-2:]) if len(domain.split(".")) >= 2 else domain
        if base_domain in DOMAIN_RELIABILITY:
            return {"score": DOMAIN_RELIABILITY[base_domain], "domain": base_domain, "source": "known"}
        return {"score": 0.40, "domain": domain, "source": "unknown"}

    async def check_recency(self, url: str) -> dict[str, Any]:
        await asyncio.sleep(0.01)
        return {
            "is_recent": True,
            "last_checked": datetime.now().isoformat(),
            "days_since_check": 0,
        }

    async def check_relevance(self, url: str, topic: str = "") -> dict[str, Any]:
        await asyncio.sleep(0.01)
        score = 0.7
        path = url.split("://")[-1].split("/")[1:] if "://" in url else url.split("/")
        path_terms = " ".join(path).lower()
        if topic and topic.lower() in path_terms:
            score = 0.9
        return {
            "score": score,
            "topic": topic,
            "path_terms": path_terms[:100],
        }

    async def get_source_score(self, url: str) -> float:
        reliability = await self.check_reliability(url)
        recency = await self.check_recency(url)
        relevance = await self.check_relevance(url)
        score = (
            reliability["score"] * 0.5
            + (1.0 if recency["is_recent"] else 0.3) * 0.25
            + relevance["score"] * 0.25
        )
        return round(score, 4)