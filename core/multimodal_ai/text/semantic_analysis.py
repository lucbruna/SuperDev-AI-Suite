from typing import Any, Optional
from collections import Counter


class SemanticAnalyzer:
    def __init__(self) -> None:
        self._sentiment_lexicon: dict[str, float] = {
            "good": 0.5, "great": 0.8, "excellent": 1.0, "amazing": 0.9,
            "fantastic": 0.9, "wonderful": 0.8, "happy": 0.7, "positive": 0.6,
            "success": 0.8, "profit": 0.7, "growth": 0.6, "improved": 0.6,
            "increase": 0.5, "strong": 0.5, "efficient": 0.6, "productive": 0.6,
            "bad": -0.5, "poor": -0.6, "terrible": -1.0, "awful": -0.9,
            "horrible": -0.9, "negative": -0.6, "failure": -0.8, "loss": -0.7,
            "decline": -0.6, "decrease": -0.5, "weak": -0.5, "slow": -0.3,
            "problem": -0.5, "issue": -0.4, "error": -0.6, "defect": -0.7,
            "delay": -0.4, "damage": -0.6, "not": -0.3, "no": -0.2,
        }
        self._topic_keywords: dict[str, list[str]] = {
            "sales": ["sell", "sold", "revenue", "customer", "order", "deal"],
            "finance": ["budget", "cost", "expense", "profit", "revenue", "financial"],
            "inventory": ["stock", "warehouse", "supply", "product", "item"],
            "production": ["manufacturing", "output", "line", "machine", "produce"],
            "hr": ["employee", "staff", "hire", "training", "benefit"],
        }

    def analyze_semantics(self, text: str) -> dict[str, Any]:
        return {
            "sentiment": self.get_sentiment(text),
            "meanings": self.extract_meanings(text),
            "relations": self.find_relations(text),
            "topics": self._detect_topics(text),
        }

    def extract_meanings(self, text: str) -> dict[str, Any]:
        words = __import__("re").findall(r"\b\w+\b", text.lower())
        freq = Counter(words)
        return {
            "key_terms": [{"word": w, "frequency": c} for w, c in freq.most_common(10)],
            "total_unique_words": len(freq),
            "dominant_topic": self._detect_topics(text),
        }

    def find_relations(self, text: str) -> list[dict[str, str]]:
        relations: list[dict[str, str]] = []
        patterns = [
            (r"\b(\w+)\s+(?:is|are|was|were)\s+(\w+)", "is_a"),
            (r"\b(\w+)\s+(?:has|have|had)\s+(\w+)", "has"),
            (r"\b(\w+)\s+(?:leads?|leads? to|results? in|causes?)\s+(\w+)", "causes"),
            (r"\b(\w+)\s+(?:depends? on|relies? on|requires?)\s+(\w+)", "depends_on"),
        ]
        for pattern, rel_type in patterns:
            import re
            for match in re.finditer(pattern, text, re.IGNORECASE):
                relations.append({
                    "subject": match.group(1),
                    "object": match.group(2),
                    "type": rel_type,
                })
        return relations

    def get_sentiment(self, text: str) -> dict[str, Any]:
        words = __import__("re").findall(r"\b\w+\b", text.lower())
        negation = False
        score = 0.0
        count = 0
        for word in words:
            if word in {"not", "no", "never", "neither", "nor", "none"}:
                negation = not negation
                continue
            if word in self._sentiment_lexicon:
                val = self._sentiment_lexicon[word]
                if negation:
                    val = -val
                    negation = False
                score += val
                count += 1
        avg = score / max(count, 1)
        if avg > 0.2:
            label = "positive"
        elif avg < -0.2:
            label = "negative"
        else:
            label = "neutral"
        return {
            "score": round(avg, 3),
            "label": label,
            "confidence": min(abs(avg) + 0.3, 1.0) if avg != 0 else 0.0,
        }

    def summarize(self, text: str, max_sentences: int = 3) -> str:
        import re
        sentences = [s.strip() for s in re.split(r"[.!?]+", text) if s.strip()]
        if len(sentences) <= max_sentences:
            return text
        scored: list[tuple[int, str]] = []
        for i, s in enumerate(sentences):
            words = re.findall(r"\b\w+\b", s.lower())
            score_val = sum(
                abs(self._sentiment_lexicon.get(w, 0)) for w in words
            )
            scored.append((score_val, i, s))
        scored.sort(key=lambda x: x[0], reverse=True)
        selected = sorted(scored[:max_sentences], key=lambda x: x[1])
        return " ".join(s[2] for s in selected)

    def _detect_topics(self, text: str) -> list[dict[str, Any]]:
        text_lower = text.lower()
        topics: list[dict[str, Any]] = []
        for topic, keywords in self._topic_keywords.items():
            matches = sum(1 for kw in keywords if kw in text_lower)
            if matches > 0:
                topics.append({"topic": topic, "relevance": matches / len(keywords)})
        topics.sort(key=lambda x: x["relevance"], reverse=True)
        return topics
