from __future__ import annotations

from ..consolidation_engine import ConsolidationEngine
from ..learning import Learning
from ..reinforcement import Reinforcement
from ..pattern_detector import PatternDetector
from ..duplication_detector import DuplicationDetector
from ..summarizer import Summarizer
from ..abstraction import Abstraction
from ..knowledge_merger import KnowledgeMerger
from ..concept_merger import ConceptMerger


class TestConsolidationEngine:
    def setup_method(self) -> None:
        self.engine = ConsolidationEngine()

    def test_consolidate(self) -> None:
        entries = [{"id": "1", "content": "hello", "type": "text"}, {"id": "2", "content": "world", "type": "text"}]
        result = self.engine.consolidate(entries)
        assert "summary" in result
        assert "patterns" in result
        assert "consolidation_id" in result

    def test_snapshot(self) -> None:
        snap = self.engine.snapshot()
        assert "consolidation_count" in snap

    def test_properties(self) -> None:
        assert isinstance(self.engine.learning, Learning)
        assert isinstance(self.engine.reinforcement, Reinforcement)
        assert isinstance(self.engine.patterns, PatternDetector)
        assert isinstance(self.engine.duplicates, DuplicationDetector)
        assert isinstance(self.engine.summarizer, Summarizer)
        assert isinstance(self.engine.abstraction, Abstraction)
        assert isinstance(self.engine.knowledge, KnowledgeMerger)
        assert isinstance(self.engine.concepts, ConceptMerger)


class TestLearning:
    def setup_method(self) -> None:
        self.learning = Learning()

    def test_record_episode(self) -> None:
        self.learning.record_episode({"type": "test", "outcome": "success"})
        assert self.learning.episode_count == 1

    def test_learn_from_experience(self) -> None:
        lesson = self.learning.learn_from_experience({"type": "query", "outcome": "success", "content": "test data"})
        assert lesson["outcome"] == "success"
        assert "key_insight" in lesson

    def test_get_lessons_by_outcome(self) -> None:
        self.learning.learn_from_experience({"type": "a", "outcome": "success"})
        self.learning.learn_from_experience({"type": "b", "outcome": "failure"})
        assert len(self.learning.get_lessons_by_outcome("success")) == 1
        assert len(self.learning.get_lessons_by_outcome("failure")) == 1

    def test_clear(self) -> None:
        self.learning.record_episode({"type": "t"})
        self.learning.clear()
        assert self.learning.episode_count == 0


class TestReinforcement:
    def setup_method(self) -> None:
        self.reinf = Reinforcement()

    def test_reinforce(self) -> None:
        entry = self.reinf.reinforce("p1", 2.0)
        assert entry["pattern_id"] == "p1"
        assert entry["reinforcement"] == 2.0

    def test_reinforce_batch(self) -> None:
        entries = self.reinf.reinforce_batch(["a", "b", "c"])
        assert len(entries) == 3

    def test_get_reinforced_patterns(self) -> None:
        self.reinf.reinforce("p1", 3.0)
        self.reinf.reinforce("p2", 0.5)
        result = self.reinf.get_reinforced_patterns(threshold=1.0)
        assert "p1" in result
        assert "p2" not in result

    def test_total_reinforcement(self) -> None:
        self.reinf.reinforce("p1", 1.0)
        self.reinf.reinforce("p1", 2.0)
        assert self.reinf.total_reinforcement("p1") == 3.0

    def test_clear(self) -> None:
        self.reinf.reinforce("p1", 1.0)
        self.reinf.clear()
        assert self.reinf.cycle_count == 0


class TestPatternDetector:
    def setup_method(self) -> None:
        self.detector = PatternDetector()

    def test_detect(self) -> None:
        entries = [{"type": "a", "x": 1}, {"type": "a", "x": 2}, {"type": "b", "y": 3}]
        patterns = self.detector.detect(entries)
        assert len(patterns) >= 1

    def test_detect_sequence(self) -> None:
        entries = [{"type": "a"}, {"type": "b"}, {"type": "c"}, {"type": "a"}, {"type": "b"}, {"type": "c"}]
        seqs = self.detector.detect_sequence(entries, window=3)
        assert len(seqs) >= 1

    def test_clear(self) -> None:
        self.detector.detect([{"type": "a", "x": 1}, {"type": "a", "x": 2}])
        self.detector.clear()
        assert self.detector.pattern_count == 0


class TestDuplicationDetector:
    def setup_method(self) -> None:
        self.detector = DuplicationDetector()

    def test_deduplicate(self) -> None:
        entries = [{"id": "1", "content": "same"}, {"id": "2", "content": "same"}, {"id": "3", "content": "diff"}]
        result = self.detector.deduplicate(entries)
        assert len(result) == 2

    def test_find_duplicates(self) -> None:
        entries = [{"id": "1", "content": "x"}, {"id": "2", "content": "x"}, {"id": "3", "content": "y"}]
        dups = self.detector.find_duplicates(entries)
        assert len(dups) >= 1

    def test_similarity_score(self) -> None:
        score = self.detector.similarity_score({"a": 1, "b": 2}, {"a": 1, "c": 3})
        assert 0.0 < score < 1.0

    def test_clear(self) -> None:
        self.detector.deduplicate([{"content": "x"}, {"content": "x"}])
        self.detector.clear()
        assert self.detector.duplicate_count == 0


class TestSummarizer:
    def setup_method(self) -> None:
        self.summarizer = Summarizer()

    def test_summarize(self) -> None:
        entries = [{"content": "hello world"}, {"content": "foo bar"}]
        s = self.summarizer.summarize(entries)
        assert len(s) > 0

    def test_summarize_empty(self) -> None:
        assert self.summarizer.summarize([]) == ""

    def test_summarize_by_type(self) -> None:
        entries = [{"type": "a", "content": "x"}, {"type": "a", "content": "y"}, {"type": "b", "content": "z"}]
        result = self.summarizer.summarize_by_type(entries)
        assert "a" in result
        assert "b" in result

    def test_brief(self) -> None:
        s = self.summarizer.brief({"content": "x" * 200})
        assert len(s) <= 123

    def test_reset(self) -> None:
        self.summarizer.summarize([{"content": "x"}])
        self.summarizer.reset()
        assert self.summarizer.summary_count == 0


class TestAbstraction:
    def setup_method(self) -> None:
        self.abstraction = Abstraction()

    def test_create_abstractions(self) -> None:
        entries = [{"type": "a", "content": "x"}, {"type": "a", "content": "y"}, {"type": "b", "content": "z"}]
        result = self.abstraction.create_abstractions(entries)
        assert len(result) >= 2

    def test_merge_abstractions(self) -> None:
        abstractions = [{"type": "a", "instance_count": 3}, {"type": "b", "instance_count": 2}]
        merged = self.abstraction.merge_abstractions(abstractions)
        assert merged["instance_count"] == 5

    def test_merge_abstractions_empty(self) -> None:
        merged = self.abstraction.merge_abstractions([])
        assert merged["instance_count"] == 0

    def test_clear(self) -> None:
        self.abstraction.create_abstractions([{"type": "a", "content": "x"}])
        self.abstraction.clear()
        assert self.abstraction.abstraction_count == 0


class TestKnowledgeMerger:
    def setup_method(self) -> None:
        self.merger = KnowledgeMerger()

    def test_merge(self) -> None:
        entries = [{"topic": "t1", "content": {"a": 1}}, {"topic": "t1", "content": {"b": 2}}]
        result = self.merger.merge(entries)
        assert len(result) == 1
        assert self.merger.merge_count >= 1

    def test_merge_empty(self) -> None:
        assert self.merger.merge([]) == []

    def test_merge_by_key(self) -> None:
        entries = [{"id": "1", "group": "g1", "content": {"a": 1}}, {"id": "2", "group": "g1", "content": {"b": 2}}]
        result = self.merger.merge_by_key(entries, "group")
        assert len(result) == 1

    def test_reset(self) -> None:
        self.merger.merge([{"topic": "t", "content": {}}, {"topic": "t", "content": {}}])
        self.merger.reset()
        assert self.merger.merge_count == 0


class TestConceptMerger:
    def setup_method(self) -> None:
        self.merger = ConceptMerger()

    def test_merge_concepts(self) -> None:
        concepts = [
            {"name": "c1", "attributes": {"a": 1}, "relationships": ["r1"]},
            {"name": "c1", "attributes": {"b": 2}, "relationships": ["r2"]},
        ]
        result = self.merger.merge_concepts(concepts)
        assert len(result) == 1
        assert result[0]["instance_count"] == 2

    def test_merge_concepts_empty(self) -> None:
        assert self.merger.merge_concepts([]) == []

    def test_link_concepts(self) -> None:
        linked = self.merger.link_concepts({"name": "a", "attributes": {}}, {"name": "b", "attributes": {}})
        assert linked["linked"] is True

    def test_reset(self) -> None:
        concepts = [{"name": "c", "attributes": {}, "relationships": []}, {"name": "c", "attributes": {}, "relationships": []}]
        self.merger.merge_concepts(concepts)
        self.merger.reset()
        assert self.merger.merge_count == 0
