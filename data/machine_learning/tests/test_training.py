from __future__ import annotations

import pytest

from SuperDev.data.data_engine import DataEngine
from SuperDev.data.data_models import MLModel
from SuperDev.data.machine_learning.training import ModelTrainer


class TestSplits:
    def test_train_test_split(self) -> None:
        trainer = ModelTrainer(seed=42)
        train, test = trainer.train_test_split(list(range(10)), ratio=0.8)
        assert len(train) == 8
        assert len(test) == 2
        assert train + test == list(range(10))

    def test_train_test_split_empty(self) -> None:
        trainer = ModelTrainer(seed=42)
        assert trainer.train_test_split([]) == ([], [])

    def test_split_records_deterministic(self) -> None:
        records = [MLModel(name=f"m{i}") for i in range(10)]
        trainer = ModelTrainer(seed=7)
        train_a, test_a = trainer.split_records(records)
        trainer_b = ModelTrainer(seed=7)
        train_b, test_b = trainer_b.split_records(records)
        assert [m.name for m in train_a] == [m.name for m in train_b]
        assert len(train_a) + len(test_a) == 10


class TestKFold:
    def test_k_fold_indices(self) -> None:
        trainer = ModelTrainer(seed=1)
        folds = trainer.k_fold_indices(10, folds=5)
        assert len(folds) == 5
        for train_idx, test_idx in folds:
            assert len(test_idx) == 2
            assert len(train_idx) == 8
            assert set(train_idx) & set(test_idx) == set()

    def test_k_fold_invalid(self) -> None:
        trainer = ModelTrainer()
        assert trainer.k_fold_indices(0, folds=5) == [([], [])]

    def test_cross_validate_perfect(self) -> None:
        trainer = ModelTrainer(seed=3)
        xs = list(range(20))
        ys = [x * 2 for x in xs]

        def fit_predict(train_x, train_y, test_x):
            # perfect linear fit via least squares
            mean_x = sum(train_x) / len(train_x)
            mean_y = sum(train_y) / len(train_y)
            slope = sum((x - mean_x) * (y - mean_y) for x, y in zip(train_x, train_y, strict=False)) / sum(
                (x - mean_x) ** 2 for x in train_x
            )
            intercept = mean_y - slope * mean_x
            return [intercept + slope * x for x in test_x]

        result = trainer.cross_validate(xs, ys, fit_predict, folds=4)
        assert result["folds"] == 4
        assert result["mean_r2"] > 0.99
        assert result["mean_mae"] < 0.1

    def test_cross_validate_mismatched(self) -> None:
        trainer = ModelTrainer()
        result = trainer.cross_validate([1.0], [1.0, 2.0], lambda _a, _b, c: c)
        assert result["folds"] == 0


class TestRegressionMetrics:
    def test_r2_perfect(self) -> None:
        assert ModelTrainer.r2([1.0, 2.0, 3.0], [1.0, 2.0, 3.0]) == 1.0

    def test_r2_imperfect(self) -> None:
        r2 = ModelTrainer.r2([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 8.0])
        assert r2 < 1.0

    def test_mae(self) -> None:
        assert ModelTrainer.mae([1.0, 2.0], [1.5, 2.5]) == 0.5

    def test_rmse(self) -> None:
        # sqrt((9 + 16) / 2) = sqrt(12.5) ≈ 3.5355
        assert ModelTrainer.rmse([0.0, 0.0], [3.0, 4.0]) == pytest.approx(3.5355, abs=1e-3)

    def test_mape(self) -> None:
        # |100-110|/100 = 0.1, |200-180|/200 = 0.1 → mean = 0.1
        assert ModelTrainer.mape([100.0, 200.0], [110.0, 180.0]) == pytest.approx(0.1)

    def test_metrics_mismatched_length(self) -> None:
        trainer = ModelTrainer()
        assert trainer.r2([1.0], [1.0, 2.0]) == 0.0
        assert trainer.mae([1.0], []) == 0.0
        assert trainer.rmse([], []) == 0.0
        assert trainer.mape([1.0], [2.0, 3.0]) == 0.0

    def test_evaluate(self) -> None:
        trainer = ModelTrainer()
        result = trainer.evaluate([1.0, 2.0, 3.0], [1.0, 2.0, 4.0])
        assert set(result) == {"r2", "mae", "rmse", "mape"}
        # mae is rounded to 4 decimals: 1/3 ≈ 0.3333
        assert result["mae"] == pytest.approx(1 / 3, abs=1e-3)


class TestClassification:
    def test_confusion_matrix(self) -> None:
        cm = ModelTrainer.confusion_matrix(
            ["a", "a", "b", "b", "b"],
            ["a", "b", "b", "b", "a"],
        )
        assert cm["matrix"]["a"]["a"] == 1
        assert cm["matrix"]["a"]["b"] == 1
        assert cm["matrix"]["b"]["b"] == 2
        assert cm["matrix"]["b"]["a"] == 1

    def test_classification_report_perfect(self) -> None:
        report = ModelTrainer().classification_report(
            ["a", "a", "b", "b"],
            ["a", "a", "b", "b"],
        )
        assert report["accuracy"] == 1.0
        assert report["per_label"]["a"]["precision"] == 1.0

    def test_classification_report_imperfect(self) -> None:
        report = ModelTrainer().classification_report(
            ["a", "a", "b"],
            ["a", "b", "b"],
        )
        # accuracy rounded to 4 decimals: 2/3 ≈ 0.6667
        assert report["accuracy"] == pytest.approx(2 / 3, abs=1e-3)

    def test_classification_report_mismatched(self) -> None:
        report = ModelTrainer().classification_report(["a"], ["a", "b"])
        assert report["accuracy"] == 0.0


class TestHistory:
    def test_eval_history(self) -> None:
        trainer = ModelTrainer()
        trainer.evaluate([1.0, 2.0], [1.0, 2.0])
        trainer.cross_validate([1.0, 2.0, 3.0, 4.0], [1.0, 2.0, 3.0, 4.0],
                               lambda _a, _b, c: c, folds=2)
        assert len(trainer.history()) == 2

    def test_with_engine(self, engine: DataEngine) -> None:
        trainer = ModelTrainer(engine=engine)
        trainer.evaluate([1.0, 2.0], [1.0, 2.0])
        assert engine.metrics.get_counter("ml.evaluations") >= 1
