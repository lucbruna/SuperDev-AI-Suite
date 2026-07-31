"""Tests for the knowledge classification subsystem."""

from __future__ import annotations

import pytest

from knowledge.classification import (
    Category,
    CategoryManager,
    ClassificationEngine,
    Classifier,
    Scorer,
)


class TestCategory:
    def test_to_dict(self) -> None:
        category = Category(name="tecnologia", keywords=["python", "api"], weight=1.5)
        data = category.to_dict()
        assert data["name"] == "tecnologia"
        assert data["keywords"] == ["python", "api"]
        assert data["weight"] == 1.5


class TestCategoryManager:
    def test_add_remove_get(self) -> None:
        manager = CategoryManager()
        manager.add(Category(name="tecnologia", keywords=["python"]))
        category = manager.get("tecnologia")
        assert category is not None
        assert category.keywords == ["python"]
        assert manager.names() == ["tecnologia"]
        assert manager.remove("tecnologia") is True
        assert manager.remove("tecnologia") is False
        assert manager.get("tecnologia") is None

    def test_list_and_clear(self) -> None:
        manager = CategoryManager()
        manager.add(Category(name="a"))
        manager.add(Category(name="b"))
        assert len(manager.list()) == 2
        manager.clear()
        assert manager.list() == []


class TestScorer:
    def test_score_overlap(self) -> None:
        scorer = Scorer()
        category = Category(name="tech", keywords=["python", "api"])
        assert scorer.score("python and api", category) == pytest.approx(1.0)
        assert scorer.score("python only", category) == pytest.approx(0.5)

    def test_score_empty(self) -> None:
        scorer = Scorer()
        assert scorer.score("", Category(name="x", keywords=["k"])) == 0.0
        assert scorer.score("texto", Category(name="x")) == 0.0

    def test_scores(self) -> None:
        scorer = Scorer()
        categories = [Category(name="a", keywords=["x"]), Category(name="b", keywords=["y"])]
        assert scorer.scores("x", categories) == {"a": 1.0, "b": 0.0}


class TestClassifier:
    def test_classify(self) -> None:
        classifier = Classifier()
        classifier.category_manager.add(Category(name="tecnologia", keywords=["python", "api"]))
        classifier.category_manager.add(Category(name="financas", keywords=["receita", "trimestre"]))
        results = classifier.classify("usando python e api para o deploy")
        assert results[0]["category"] == "tecnologia"
        assert results[0]["score"] > 0

    def test_classify_threshold_and_top_k(self) -> None:
        classifier = Classifier()
        classifier.category_manager.add(Category(name="a", keywords=["palavra"]))
        results = classifier.classify("sem correspondencia", threshold=0.5)
        assert results == []
        best = classifier.best("palavra")
        assert best is not None
        assert best["category"] == "a"
        # best() returns the top result even at score 0.0 (no threshold applied)
        assert classifier.best("sem correspondencia") == {"category": "a", "score": 0.0}
        empty = Classifier()
        assert empty.best("qualquer texto") is None


class TestClassificationEngine:
    def test_add_category_and_classify(self) -> None:
        engine = ClassificationEngine()
        engine.add_category("tecnologia", ["python", "api", "deploy"])
        engine.add_category("financas", ["receita", "trimestre", "orcamento"])
        results = engine.classify("o deploy com python e a api")
        assert results[0]["category"] == "tecnologia"
        assert results[0]["score"] > 0.0
        assert engine.stats()["categories"] == ["tecnologia", "financas"]
