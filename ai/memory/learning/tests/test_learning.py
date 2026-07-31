from __future__ import annotations

from ..adaptive_learning import AdaptiveLearning
from ..evaluation import Evaluation
from ..feedback_learning import FeedbackLearning
from ..incremental_learning import IncrementalLearning
from ..learning_engine import LearningEngine
from ..model_updater import ModelUpdater
from ..pattern_learning import PatternLearning
from ..reinforcement_learning import ReinforcementLearning
from ..supervised_learning import SupervisedLearning
from ..unsupervised_learning import UnsupervisedLearning


class TestLearningEngine:
    def setup_method(self) -> None:
        self.engine = LearningEngine()

    def test_learn(self) -> None:
        result = self.engine.learn([{"type": "a"}, {"type": "a"}, {"type": "b"}])
        assert "patterns" in result
        assert "learning_id" in result

    def test_snapshot(self) -> None:
        snap = self.engine.snapshot()
        assert "learning_count" in snap

    def test_properties(self) -> None:
        assert isinstance(self.engine.feedback, FeedbackLearning)
        assert isinstance(self.engine.reinforcement, ReinforcementLearning)
        assert isinstance(self.engine.supervised, SupervisedLearning)
        assert isinstance(self.engine.unsupervised, UnsupervisedLearning)
        assert isinstance(self.engine.pattern, PatternLearning)
        assert isinstance(self.engine.adaptive, AdaptiveLearning)
        assert isinstance(self.engine.incremental, IncrementalLearning)
        assert isinstance(self.engine.updater, ModelUpdater)
        assert isinstance(self.engine.evaluation, Evaluation)


class TestFeedbackLearning:
    def setup_method(self) -> None:
        self.fb = FeedbackLearning()

    def test_record(self) -> None:
        s = self.fb.record("q", "r", 0.8)
        assert s.query == "q"
        assert s.feedback == 0.8
        assert self.fb.sample_count == 1

    def test_positive_samples(self) -> None:
        self.fb.record("q1", "r1", 0.9)
        self.fb.record("q2", "r2", 0.3)
        assert len(self.fb.positive_samples(0.5)) == 1

    def test_average_feedback(self) -> None:
        self.fb.record("q", "r", 0.5)
        self.fb.record("q", "r", 1.0)
        assert self.fb.average_feedback() == 0.75

    def test_clear(self) -> None:
        self.fb.record("q", "r", 1.0)
        self.fb.clear()
        assert self.fb.sample_count == 0


class TestReinforcementLearning:
    def setup_method(self) -> None:
        self.rl = ReinforcementLearning(learning_rate=0.5)

    def test_act(self) -> None:
        action = self.rl.act("s1", ["a", "b"])
        assert action in ("a", "b")
        assert self.rl.cycle_count == 1

    def test_reward(self) -> None:
        self.rl.reward("s1", "a", 1.0)
        assert self.rl.get_q_value("s1", "a") > 0

    def test_clear(self) -> None:
        self.rl.reward("s", "a", 1.0)
        self.rl.clear()
        assert self.rl.get_q_value("s", "a") == 0.0


class TestSupervisedLearning:
    def setup_method(self) -> None:
        self.sl = SupervisedLearning()

    def test_add_and_predict(self) -> None:
        self.sl.add_example({"a": 1}, "x")
        self.sl.add_example({"b": 2}, "y")
        pred = self.sl.predict({"a": 1})
        assert pred is not None

    def test_predict_no_data(self) -> None:
        assert self.sl.predict({"a": 1}) is None

    def test_add_batch(self) -> None:
        self.sl.add_batch([({"a": 1}, "x"), ({"b": 2}, "y")])
        assert len(self.sl.training_data) == 2

    def test_clear(self) -> None:
        self.sl.add_example({"a": 1}, "x")
        self.sl.clear()
        assert self.sl.train_count == 0


class TestUnsupervisedLearning:
    def setup_method(self) -> None:
        self.ul = UnsupervisedLearning()

    def test_cluster(self) -> None:
        items = [{"type": "a"}, {"type": "a"}, {"type": "b"}]
        groups = self.ul.cluster(items)
        assert "a" in groups
        assert "b" in groups

    def test_cluster_sizes(self) -> None:
        self.ul.cluster([{"type": "a"}, {"type": "a"}, {"type": "b"}])
        sizes = self.ul.cluster_sizes()
        assert sizes["a"] == 2

    def test_get_cluster(self) -> None:
        self.ul.cluster([{"type": "a"}, {"type": "a"}])
        assert len(self.ul.get_cluster("a")) == 2

    def test_clear(self) -> None:
        self.ul.cluster([{"type": "a"}])
        self.ul.clear()
        assert self.ul.cluster_count == 0


class TestPatternLearning:
    def setup_method(self) -> None:
        self.pl = PatternLearning()

    def test_learn(self) -> None:
        data = [{"type": "a"}, {"type": "a"}, {"type": "b"}]
        patterns = self.pl.learn(data)
        assert len(patterns) >= 1

    def test_learn_sequence(self) -> None:
        seqs = self.pl.learn_sequence(["a", "b", "a", "b"])
        assert len(seqs) >= 1

    def test_clear(self) -> None:
        self.pl.learn([{"type": "a"}, {"type": "a"}])
        self.pl.clear()
        assert self.pl.pattern_count == 0


class TestAdaptiveLearning:
    def setup_method(self) -> None:
        self.al = AdaptiveLearning(initial_rate=0.5)

    def test_adapt_high_performance(self) -> None:
        rate = self.al.adapt(0.9)
        assert rate > 0.5

    def test_adapt_low_performance(self) -> None:
        rate = self.al.adapt(0.2)
        assert rate < 0.5

    def test_reset(self) -> None:
        self.al.adapt(0.9)
        self.al.reset()
        assert self.al.learning_rate == 0.5


class TestIncrementalLearning:
    def setup_method(self) -> None:
        self.il = IncrementalLearning()

    def test_update(self) -> None:
        count = self.il.update([{"type": "a"}, {"type": "b"}])
        assert count == 2
        assert self.il.update_count == 1

    def test_update_single(self) -> None:
        self.il.update_single({"type": "a"})
        assert len(self.il.data) == 1

    def test_summary(self) -> None:
        self.il.update([{"type": "a"}, {"type": "b"}])
        s = self.il.summary()
        assert s["total_samples"] == 2

    def test_clear(self) -> None:
        self.il.update([{"type": "a"}])
        self.il.clear()
        assert self.il.update_count == 0


class TestModelUpdater:
    def setup_method(self) -> None:
        self.mu = ModelUpdater()

    def test_update(self) -> None:
        v = self.mu.update([{"type": "a"}])
        assert v == 1
        assert self.mu.update_count == 1

    def test_rollback(self) -> None:
        self.mu.update([])
        self.mu.update([])
        assert self.mu.rollback(1) is True
        assert self.mu.version == 1
        assert self.mu.rollback(5) is False

    def test_clear(self) -> None:
        self.mu.update([])
        self.mu.clear()
        assert self.mu.version == 0


class TestEvaluation:
    def setup_method(self) -> None:
        self.eval = Evaluation()

    def test_evaluate(self) -> None:
        acc = self.eval.evaluate(["a", "b", "a"], ["a", "b", "b"])
        assert acc > 0.5
        assert self.eval.eval_count == 1

    def test_precision_recall(self) -> None:
        result = self.eval.precision_recall([True, True, False], [True, False, False])
        assert "precision" in result
        assert "recall" in result

    def test_clear(self) -> None:
        self.eval.evaluate(["a"], ["a"])
        self.eval.clear()
        assert self.eval.eval_count == 0
