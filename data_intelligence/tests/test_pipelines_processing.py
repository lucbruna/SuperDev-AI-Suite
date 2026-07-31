"""Tests for the pipelines and processing subsystems (Volume 22, Fase 3)."""

from __future__ import annotations

from data_intelligence.data_context import DataIntelligenceContext
from data_intelligence.data_events import DataIntelligenceEvents
from data_intelligence.data_metrics import DataIntelligenceMetrics
from data_intelligence.pipelines.base import PipelineError
from data_intelligence.pipelines.cleaning import CleaningStage
from data_intelligence.pipelines.extraction import ExtractionStage
from data_intelligence.pipelines.indicator import IndicatorStage
from data_intelligence.pipelines.orchestrator import PipelineOrchestrator
from data_intelligence.pipelines.sink import SinkStage
from data_intelligence.pipelines.transformation import TransformationStage
from data_intelligence.processing.base import ProcessingError
from data_intelligence.processing.chain import ProcessingChain
from data_intelligence.processing.cleaning import (DefaultFiller,
                                                   TrimProcessor)
from data_intelligence.processing.engine import ProcessingEngine
from data_intelligence.processing.enrichment import (CustomerSegmenter,
                                                     LocationEnricher)
from data_intelligence.processing.normalization import (EmailNormalizer,
                                                        NameNormalizer,
                                                        UfNormalizer)
from data_intelligence.processing.validation import (EmailValidator,
                                                     RequiredFieldValidator)


def make_orchestrator() -> PipelineOrchestrator:
    events = DataIntelligenceEvents()
    metrics = DataIntelligenceMetrics()
    return PipelineOrchestrator(events=events, metrics=metrics,
                                config=None,
                                context=DataIntelligenceContext())


def make_processing() -> ProcessingEngine:
    events = DataIntelligenceEvents()
    metrics = DataIntelligenceMetrics()
    return ProcessingEngine(events=events, metrics=metrics, config=None,
                            context=DataIntelligenceContext())


class TestPipelineStages:
    def test_cleaning_dedupe_required_trim(self) -> None:
        stage = CleaningStage(dedupe_key="id", required=["email"],
                              defaults={"uf": "SP"})
        records = [
            {"id": 1, "name": "  Ana  ", "email": "a@x.com"},
            {"id": 1, "name": "Dup", "email": "a@x.com"},
            {"id": 2, "email": ""},
            {"id": 3, "name": "Bia", "email": "b@x.com"},
        ]
        out, context = stage.run(records, {})
        assert len(out) == 2
        assert out[0]["name"] == "Ana"
        assert out[0]["uf"] == "SP"
        assert out[1]["email"] == "b@x.com"
        assert context["cleaning"] == {"duplicates": 1, "incomplete": 1}

    def test_transformation(self) -> None:
        stage = TransformationStage(rename={"name": "cliente"},
                                    casts={"valor": "number"},
                                    drop=["internal"])
        out, _ = stage.run(
            [{"cliente": "Ana", "valor": "10.5", "internal": "x"}], {})
        assert out == [{"name": "Ana", "valor": 10.5}]

    def test_indicator_aggregations(self) -> None:
        stage = IndicatorStage(value_field="valor",
                               aggregations=["total", "count", "average",
                                             "min", "max"])
        records = [{"valor": 10}, {"valor": 20}, {"valor": 30}]
        out, context = stage.run(records, {})
        indicator = out[0]
        assert indicator["total"] == 60
        assert indicator["count"] == 3
        assert indicator["average"] == 20
        assert indicator["min"] == 10
        assert indicator["max"] == 30
        context_indicator = context["indicators"][0]
        assert context_indicator["total"] == 60
        assert "tags" not in context_indicator  # context keeps raw indicator
        assert indicator["tags"] == ["indicator"]  # output is tagged

    def test_indicator_grouped(self) -> None:
        stage = IndicatorStage(value_field="v", group_by="uf")
        records = [{"uf": "SP", "v": 10}, {"uf": "SP", "v": 20},
                   {"uf": "RJ", "v": 5}]
        out, _ = stage.run(records, {})
        by_uf = {r["uf"]: r["total"] for r in out}
        assert by_uf == {"RJ": 5.0, "SP": 30.0}

    def test_indicator_empty(self) -> None:
        stage = IndicatorStage(value_field="v")
        out, _ = stage.run([], {})
        assert out[0]["total"] == 0.0
        assert out[0]["count"] == 0

    def test_extraction(self) -> None:
        class FakeCollector:
            def fetch(self, source_id, tags=None):
                class R:
                    data = {"v": 1}
                return [R()]

        stage = ExtractionStage(collector=FakeCollector(), source_id="s1")
        out, context = stage.run([], {})
        assert out == [{"v": 1}]
        assert context["extracted_count"] == 1

    def test_extraction_requires_config(self) -> None:
        stage = ExtractionStage()
        try:
            stage.run([], {})
            raised = False
        except PipelineError:
            raised = True
        assert raised is True

    def test_sink_none(self) -> None:
        stage = SinkStage(destination="none")
        out, context = stage.run([{"a": 1}], {})
        assert len(out) == 1
        assert context["sink"]["written"] == 1

    def test_sink_requires_sink(self) -> None:
        stage = SinkStage(destination="dashboard")
        try:
            stage.run([], {})
            raised = False
        except PipelineError:
            raised = True
        assert raised is True

    def test_sink_writes(self) -> None:
        class FakeSink:
            def write(self, records, destination):
                return {"written": len(records), "destination": destination}

        stage = SinkStage(destination="dashboard", sink=FakeSink(),
                          target="dash-1")
        out, context = stage.run([{"a": 1}, {"a": 2}], {})
        assert context["sink"]["written"] == 2
        assert context["sink"]["destination"] == "dash-1"


class TestPipelineOrchestrator:
    def test_full_pipeline_vendas(self) -> None:
        """ERP -> extrair vendas -> limpar -> indicadores -> dashboard."""
        orch = make_orchestrator()

        class FakeCollector:
            def fetch(self, source_id, tags=None):
                class R:
                    data = {"produto": "X", "valor": 100}
                return [R(), R()]

        class FakeDashboard:
            written: list[dict] = []

            def write(self, records, destination):
                self.written = list(records)
                return {"written": len(records)}

        dash = FakeDashboard()
        orch.add_pipeline("p-vendas", "Vendas", [
            {"stage": "extraction", "collector": FakeCollector(),
             "source_id": "s-erp"},
            {"stage": "cleaning", "required": ["produto"]},
            {"stage": "transformation",
             "casts": {"valor": "number"}},
            {"stage": "indicator", "value_field": "valor",
             "aggregations": ["total", "count"]},
            {"stage": "sink", "destination": "dashboard",
             "sink": dash, "target": "dash-exec"},
        ])
        result = orch.run("p-vendas")
        assert result["status"] == "completed"
        assert result["output_count"] == 1
        assert result["context"]["indicators"][0]["total"] == 200
        assert len(dash.written) == 1
        latest = orch.latest("p-vendas")
        assert latest is not None and latest["status"] == "completed"

    def test_unknown_pipeline(self) -> None:
        orch = make_orchestrator()
        try:
            orch.run("ghost")
            raised = False
        except PipelineError:
            raised = True
        assert raised is True

    def test_add_pipeline_and_stats(self) -> None:
        orch = make_orchestrator()
        orch.add_pipeline("p1", "Pipeline 1",
                          [{"stage": "cleaning"}])
        assert "p1" in orch.specs
        result = orch.run("p1", [{"a": " x "}])
        assert result["status"] == "completed"
        stats = orch.stats()
        assert stats["pipelines"] == ["p1"]
        assert stats["runs"] == 1
        assert stats["last_status"]["p1"] == "completed"
        assert orch.remove("p1") is True
        assert orch.remove("p1") is False

    def test_unknown_stage_type(self) -> None:
        orch = make_orchestrator()
        orch.add_pipeline("bad", "Bad", [{"stage": "nope"}])
        result = orch.run("bad")
        assert result["status"] == "failed"
        assert "error" in result["context"]

    def test_run_all(self) -> None:
        orch = make_orchestrator()
        orch.add_pipeline("p1", "P1", [{"stage": "cleaning"}])
        orch.add_pipeline("p2", "P2", [{"stage": "cleaning"}])
        results = orch.run_all()
        assert len(results) == 2
        assert all(r["status"] == "completed" for r in results)

    def test_disabled_pipeline(self) -> None:
        orch = make_orchestrator()
        spec = orch.add_pipeline("off", "Off", [{"stage": "cleaning"}])
        spec.enabled = False
        result = orch.run("off")
        assert result["status"] == "skipped"


class TestProcessingNormalization:
    def test_name_email_uf_chain(self) -> None:
        """'JOAO SILVA / joao@gmail.com / SP' -> cleaned + segment."""
        chain = ProcessingChain([
            NameNormalizer(),
            EmailNormalizer(),
            UfNormalizer(field="uf", output="state"),
            CustomerSegmenter(purchases_field="purchases"),
        ])
        record = {"name": "JOAO SILVA", "email": "Joao@GMAIL.com ",
                  "uf": "sp", "purchases": 3}
        out = chain.apply(record)
        assert out["name"] == "Joao Silva"
        assert out["email"] == "joao@gmail.com"
        assert out["state"] == "São Paulo"
        assert out["segment"] == "Cliente recorrente"

    def test_high_value_segment(self) -> None:
        chain = ProcessingChain([CustomerSegmenter()])
        out = chain.apply({"purchases": 1, "total_value": 9999})
        assert out["segment"] == "Cliente alto valor"

    def test_new_customer(self) -> None:
        chain = ProcessingChain([CustomerSegmenter()])
        out = chain.apply({"purchases": 1, "total_value": 100})
        assert out["segment"] == "Cliente novo"

    def test_phone_and_trim(self) -> None:
        from data_intelligence.processing.normalization import PhoneNormalizer
        chain = ProcessingChain([TrimProcessor(), PhoneNormalizer()])
        out = chain.apply({"phone": " (11) 91234-5678 "})
        assert out["phone"] == "11912345678"

    def test_location_enricher(self) -> None:
        chain = ProcessingChain([LocationEnricher()])
        assert chain.apply({"uf": "MG"})["region"] == "southeast"
        assert chain.apply({"uf": "AM"})["region"] == "north"
        assert "region" not in chain.apply({"uf": "XX"})

    def test_defaults_and_drop_empty(self) -> None:
        from data_intelligence.processing.cleaning import DropEmptyProcessor
        chain = ProcessingChain([DefaultFiller({"uf": "SP"}),
                                 DropEmptyProcessor()])
        out = chain.apply({"name": "", "uf": None, "keep": 1})
        assert out == {"uf": "SP", "keep": 1}


class TestProcessingValidation:
    def test_email_validator_ok(self) -> None:
        chain = ProcessingChain([EmailValidator()])
        assert chain.apply({"email": "ana@x.com"})["email"] == "ana@x.com"

    def test_email_validator_rejects(self) -> None:
        chain = ProcessingChain([EmailValidator()])
        try:
            chain.apply({"email": "nao-e-email"})
            raised = False
        except ProcessingError:
            raised = True
        assert raised is True
        assert len(chain.rejected) == 1

    def test_required_field(self) -> None:
        chain = ProcessingChain([RequiredFieldValidator(["cpf"])])
        try:
            chain.apply({"nome": "Ana"})
            raised = False
        except ProcessingError:
            raised = True
        assert raised is True

    def test_apply_many_skips(self) -> None:
        chain = ProcessingChain([EmailValidator()])
        out = chain.apply_many([{"email": "ok@x.com"},
                                {"email": "ruim"}])
        assert len(out) == 1
        assert len(chain.rejected) == 1

    def test_apply_many_keep_rejected(self) -> None:
        chain = ProcessingChain([EmailValidator()])
        out = chain.apply_many([{"email": "ok@x.com"}, {"email": "ruim"}],
                               keep_rejected=True)
        assert len(out) == 2


class TestProcessingEngine:
    def test_build_and_process(self) -> None:
        engine = make_processing()
        engine.register_chain("cliente", engine.build_chain(
            ["trim", "name", "email", "segment"]))
        result = engine.process("cliente", [
            {"name": " JOAO ", "email": "J@X.com", "purchases": 5},
            {"name": " BIA ", "email": "b@x.com", "purchases": 1},
        ])
        assert result["input"] == 2
        assert result["output"] == 2
        assert result["rejected"] == 0
        assert result["records"][0]["segment"] == "Cliente recorrente"

    def test_build_chain_params(self) -> None:
        engine = make_processing()
        chain = engine.build_chain(["segment"],
                                   segment={"high_value_threshold": 50})
        assert chain.apply({"total_value": 60})["segment"] == "Cliente alto valor"

    def test_unknown_chain(self) -> None:
        engine = make_processing()
        try:
            engine.process("ghost", [])
            raised = False
        except ValueError:
            raised = True
        assert raised is True

    def test_unknown_processor(self) -> None:
        engine = make_processing()
        try:
            engine.build_chain(["magic"])
            raised = False
        except ValueError:
            raised = True
        assert raised is True

    def test_process_many_chains(self) -> None:
        engine = make_processing()
        engine.register_chain("a", engine.build_chain(["trim"]))
        engine.register_chain("b", engine.build_chain(["name"]))
        summary = engine.process_many([{"name": " ana "}])
        assert set(summary["chains"]) == {"a", "b"}
        assert summary["chains"]["a"]["output"] == 1
        assert engine.stats()["chains"] == ["a", "b"]
