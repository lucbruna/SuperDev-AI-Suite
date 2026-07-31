"""Data Platform — Comprehensive test suite."""

# Core models
from data_platform.analytics.engine import AnalyticsEngine
from data_platform.analytics.models import AnalyticsQuery, Dashboard, QueryType

# Core support
from data_platform.data_config import DataPlatformConfig
from data_platform.data_context import DataPlatformContext

# Core engine
from data_platform.data_engine import DataPlatformEngine
from data_platform.data_factory import DataPlatformFactory
from data_platform.data_logger import DataLogLevel, DataPlatformLogger
from data_platform.data_metrics import DataPlatformMetrics
from data_platform.data_models import (
    DataCatalogEntry,
    DataPipeline,
    DataRecord,
    DataSchema,
    DataSource,
    PipelineStatus,
)
from data_platform.data_runtime import DataPlatformRuntime
from data_platform.data_security import DataAccessLevel, DataPlatformSecurity
from data_platform.etl.engine import ETLEngine
from data_platform.etl.models import ETLPipeline, ETLStatus, ETLStep, StepType
from data_platform.governance.engine import GovernanceEngine
from data_platform.governance.models import (
    AccessLevel,
    AccessPolicy,
    AuditEntry,
    ComplianceRule,
    ComplianceStandard,
    RetentionPolicy,
)

# Subsystem engines
from data_platform.ingestion.engine import IngestionEngine
from data_platform.ingestion.models import Connector, ConnectorType, IngestionStatus
from data_platform.knowledge_graph.engine import KnowledgeGraphEngine
from data_platform.knowledge_graph.models import Entity, EntityType, Relation, RelationType
from data_platform.machine_learning.engine import MLEngine
from data_platform.machine_learning.models import MLModel, ModelStatus, ModelType
from data_platform.processing.engine import ProcessingEngine
from data_platform.processing.models import ProcessingJob, ProcessingStatus, TransformRule, TransformType
from data_platform.quality.engine import QualityEngine
from data_platform.quality.models import QualityStatus
from data_platform.storage.engine import StorageEngine
from data_platform.storage.models import DataPartition as StoragePartition
from data_platform.storage.models import StorageBucket, StorageType, StoredObject
from data_platform.streaming.engine import StreamingEngine
from data_platform.streaming.models import StreamConsumer, StreamEvent, StreamTopic

# ========== Core Engine Tests ==========


class TestCoreEngine:
    def test_register_source(self):
        engine = DataPlatformEngine()
        src = DataSource(source_id="S001", name="ERP DB")
        engine.register_source(src)
        assert engine.get_source("S001") is src

    def test_ingest_record(self):
        engine = DataPlatformEngine()
        rec = DataRecord(record_id="R001", dataset="sales", payload={"amount": 100})
        engine.ingest_record(rec)
        assert engine.get_record("R001") is rec

    def test_query_records(self):
        engine = DataPlatformEngine()
        engine.ingest_record(DataRecord(record_id="R001", dataset="sales", payload={"region": "north"}))
        engine.ingest_record(DataRecord(record_id="R002", dataset="sales", payload={"region": "south"}))
        engine.ingest_record(DataRecord(record_id="R003", dataset="finance", payload={"region": "north"}))
        results = engine.query_records("sales", {"region": "north"})
        assert len(results) == 1

    def test_pipeline_lifecycle(self):
        engine = DataPlatformEngine()
        p = DataPipeline(pipeline_id="P001", name="ETL Daily")
        engine.create_pipeline(p)
        assert engine.start_pipeline("P001") is True
        assert p.status == PipelineStatus.RUNNING
        assert engine.complete_pipeline("P001", 1000) is True
        assert p.status == PipelineStatus.COMPLETED
        assert p.records_processed == 1000

    def test_pipeline_fail(self):
        engine = DataPlatformEngine()
        p = DataPipeline(pipeline_id="P001")
        engine.create_pipeline(p)
        engine.start_pipeline("P001")
        assert engine.fail_pipeline("P001") is True
        assert p.status == PipelineStatus.FAILED

    def test_schema(self):
        engine = DataPlatformEngine()
        s = DataSchema(
            schema_id="SC001", name="Sales Schema", dataset="sales", fields=[{"name": "amount", "type": "float"}]
        )
        engine.register_schema(s)
        assert engine.get_schema("SC001") is s

    def test_catalog(self):
        engine = DataPlatformEngine()
        entry = DataCatalogEntry(entry_id="E001", dataset="sales", description="Sales data", tags=["revenue"])
        engine.add_catalog_entry(entry)
        results = engine.search_catalog("sales")
        assert len(results) == 1

    def test_stats(self):
        engine = DataPlatformEngine()
        engine.register_source(DataSource(source_id="S001"))
        engine.ingest_record(DataRecord(record_id="R001", dataset="test"))
        stats = engine.get_stats()
        assert stats["sources"] == 1
        assert stats["records"] == 1


# ========== Ingestion Tests ==========


class TestIngestionSubsystem:
    def test_register_connector(self):
        engine = IngestionEngine()
        conn = Connector(connector_id="C001", name="PostgreSQL", connector_type=ConnectorType.DATABASE)
        engine.register_connector(conn)
        assert engine.get_connector("C001") is conn

    def test_create_batch(self):
        engine = IngestionEngine()
        engine.register_connector(Connector(connector_id="C001"))
        batch = engine.create_batch("C001", [{"id": 1}, {"id": 2}])
        assert batch.record_count == 2

    def test_complete_batch(self):
        engine = IngestionEngine()
        engine.register_connector(Connector(connector_id="C001"))
        batch = engine.create_batch("C001", [{"id": 1}])
        assert engine.complete_batch(batch.batch_id) is True
        assert batch.status == IngestionStatus.COMPLETED

    def test_stats(self):
        engine = IngestionEngine()
        engine.register_connector(Connector(connector_id="C001", records_ingested=50))
        stats = engine.get_stats()
        assert stats["total_records_ingested"] == 50


# ========== Storage Tests ==========


class TestStorageSubsystem:
    def test_create_bucket(self):
        engine = StorageEngine()
        bucket = StorageBucket(bucket_id="B001", name="DataLake", storage_type=StorageType.DATA_LAKE)
        engine.create_bucket(bucket)
        assert engine.get_bucket("B001") is bucket

    def test_store_object(self):
        engine = StorageEngine()
        engine.create_bucket(StorageBucket(bucket_id="B001", capacity_bytes=1000000))
        obj = StoredObject(object_id="O001", bucket_id="B001", key="data/file.json", size_bytes=100)
        engine.store_object(obj)
        bucket = engine.get_bucket("B001")
        assert bucket.used_bytes == 100

    def test_delete_object(self):
        engine = StorageEngine()
        engine.create_bucket(StorageBucket(bucket_id="B001", capacity_bytes=1000000))
        obj = StoredObject(object_id="O001", bucket_id="B001", size_bytes=100)
        engine.store_object(obj)
        assert engine.delete_object("O001") is True
        assert engine.get_object("O001") is None

    def test_partition(self):
        engine = StorageEngine()
        p = StoragePartition(partition_id="P001", dataset="sales", key="2024-01")
        engine.create_partition(p)
        assert engine.get_partition("P001") is p

    def test_utilization(self):
        bucket = StorageBucket(bucket_id="B001", capacity_bytes=1000, used_bytes=250)
        assert bucket.utilization_pct == 25.0


# ========== Processing Tests ==========


class TestProcessingSubsystem:
    def test_transform_filter(self):
        engine = ProcessingEngine()
        rule = TransformRule(
            rule_id="R001", transform_type=TransformType.FILTER, config={"field": "status", "value": "active"}
        )
        records = [{"status": "active"}, {"status": "inactive"}, {"status": "active"}]
        result = engine.transform_records(records, [rule])
        assert len(result) == 2

    def test_transform_map(self):
        engine = ProcessingEngine()
        rule = TransformRule(
            rule_id="R001", transform_type=TransformType.MAP, config={"mapping": {"old_name": "new_name"}}
        )
        records = [{"old_name": "test"}]
        result = engine.transform_records(records, [rule])
        assert "new_name" in result[0]

    def test_transform_deduplicate(self):
        engine = ProcessingEngine()
        rule = TransformRule(rule_id="R001", transform_type=TransformType.DEDUPLICATE, config={"key": "id"})
        records = [{"id": 1}, {"id": 1}, {"id": 2}]
        result = engine.transform_records(records, [rule])
        assert len(result) == 2

    def test_aggregate(self):
        engine = ProcessingEngine()
        records = [
            {"region": "north", "amount": 100},
            {"region": "north", "amount": 200},
            {"region": "south", "amount": 150},
        ]
        result = engine.aggregate_records(records, "region", "amount", "sum")
        assert len(result) == 2
        north = [r for r in result if r["region"] == "north"][0]
        assert north["sum_amount"] == 300

    def test_job_lifecycle(self):
        engine = ProcessingEngine()
        job = ProcessingJob(job_id="J001", name="Process Sales", input_count=100)
        engine.create_job(job)
        engine.start_job("J001")
        assert job.status == ProcessingStatus.RUNNING
        engine.complete_job("J001", 95)
        assert job.status == ProcessingStatus.COMPLETED


# ========== Streaming Tests ==========


class TestStreamingSubsystem:
    def test_create_topic(self):
        engine = StreamingEngine()
        topic = StreamTopic(topic_id="T001", name="events")
        engine.create_topic(topic)
        assert engine.get_topic("T001") is topic

    def test_produce_consume(self):
        engine = StreamingEngine()
        engine.create_topic(StreamTopic(topic_id="T001"))
        event = StreamEvent(event_id="E001", topic_id="T001", payload={"action": "click"})
        engine.produce_event(event)
        consumer = StreamConsumer(consumer_id="C001", topic_id="T001")
        engine.create_consumer(consumer)
        events = engine.consume_events("T001", "C001")
        assert len(events) == 1

    def test_topic_message_count(self):
        engine = StreamingEngine()
        engine.create_topic(StreamTopic(topic_id="T001"))
        engine.produce_event(StreamEvent(event_id="E001", topic_id="T001"))
        engine.produce_event(StreamEvent(event_id="E002", topic_id="T001"))
        assert engine.get_topic("T001").message_count == 2

    def test_pipeline(self):
        engine = StreamingEngine()
        from data_platform.streaming.models import StreamPipeline

        p = StreamPipeline(pipeline_id="P001", name="Process Events", source_topic="T001", target_topic="T002")
        engine.create_pipeline(p)
        assert engine.start_pipeline("P001") is True


# ========== ETL Tests ==========


class TestETLSubsystem:
    def test_pipeline_lifecycle(self):
        engine = ETLEngine()
        pipeline = ETLPipeline(pipeline_id="P001", name="Daily ETL")
        engine.create_pipeline(pipeline)
        engine.start_pipeline("P001")
        assert pipeline.status == ETLStatus.EXTRACTING
        engine.complete_step("P001", "step1", 500)
        engine.complete_pipeline("P001")
        assert pipeline.status == ETLStatus.COMPLETED

    def test_add_step(self):
        engine = ETLEngine()
        pipeline = ETLPipeline(pipeline_id="P001")
        engine.create_pipeline(pipeline)
        step = ETLStep(step_id="S001", name="Extract", step_type=StepType.EXTRACT, order=1)
        engine.add_step("P001", step)
        assert len(pipeline.steps) == 1

    def test_fail_pipeline(self):
        engine = ETLEngine()
        pipeline = ETLPipeline(pipeline_id="P001")
        engine.create_pipeline(pipeline)
        engine.start_pipeline("P001")
        engine.fail_pipeline("P001")
        assert pipeline.status == ETLStatus.FAILED


# ========== Quality Tests ==========


class TestQualitySubsystem:
    def test_completeness_check(self):
        engine = QualityEngine()
        records = [{"name": "Alice", "email": "a@b.com"}, {"name": "", "email": ""}]
        check = engine.check_completeness("customers", records, ["name", "email"])
        assert check.score == 0.5

    def test_uniqueness_check(self):
        engine = QualityEngine()
        records = [{"id": 1, "name": "A"}, {"id": 1, "name": "B"}, {"id": 2, "name": "C"}]
        check = engine.check_uniqueness("users", records, "id")
        assert check.score == 2.0 / 3.0

    def test_validity_check(self):
        engine = QualityEngine()
        records = [{"age": 25, "name": "Alice"}, {"age": "old", "name": 123}]
        check = engine.check_validity("people", records, {"age": "number", "name": "string"})
        assert check.status == QualityStatus.FAILED

    def test_report(self):
        engine = QualityEngine()
        engine.check_completeness("ds", [{"a": 1}], ["a"])
        report = engine.generate_report("ds")
        assert report.passed >= 0


# ========== Governance Tests ==========


class TestGovernanceSubsystem:
    def test_access_control(self):
        engine = GovernanceEngine()
        policy = AccessPolicy(policy_id="P001", user_id="U001", dataset="sales", access_level=AccessLevel.READ)
        engine.set_access(policy)
        assert engine.check_access("U001", "sales", AccessLevel.READ) is True
        assert engine.check_access("U001", "sales", AccessLevel.WRITE) is False

    def test_retention(self):
        engine = GovernanceEngine()
        policy = RetentionPolicy(policy_id="R001", dataset="logs", retention_days=90)
        engine.set_retention(policy)
        assert engine.get_retention("logs") is policy

    def test_audit_log(self):
        engine = GovernanceEngine()
        entry = AuditEntry(entry_id="A001", user_id="U001", dataset="sales", action="read")
        engine.log_access(entry)
        log = engine.get_audit_log(user_id="U001")
        assert len(log) == 1

    def test_compliance(self):
        engine = GovernanceEngine()
        rule = ComplianceRule(rule_id="CR001", standard=ComplianceStandard.LGPD, name="Data Anonymization")
        engine.add_compliance_rule(rule)
        rules = engine.get_compliance_rules(ComplianceStandard.LGPD)
        assert len(rules) == 1


# ========== Analytics Tests ==========


class TestAnalyticsSubsystem:
    def test_query_select(self):
        engine = AnalyticsEngine()
        records = [{"id": 1, "amount": 100}, {"id": 2, "amount": 200}]
        query = AnalyticsQuery(query_id="Q001", dataset="sales", query_type=QueryType.SELECT, limit=10)
        result = engine.execute_query(records, query)
        assert result.row_count == 2

    def test_query_aggregate(self):
        engine = AnalyticsEngine()
        records = [{"amount": 100}, {"amount": 200}, {"amount": 300}]
        query = AnalyticsQuery(query_id="Q001", dataset="sales", query_type=QueryType.AGGREGATE, metrics=["amount"])
        result = engine.execute_query(records, query)
        assert result.rows[0]["sum_amount"] == 600

    def test_query_group_by(self):
        engine = AnalyticsEngine()
        records = [
            {"region": "north", "amount": 100},
            {"region": "north", "amount": 200},
            {"region": "south", "amount": 150},
        ]
        query = AnalyticsQuery(
            query_id="Q001", dataset="sales", query_type=QueryType.GROUP_BY, group_by=["region"], metrics=["amount"]
        )
        result = engine.execute_query(records, query)
        assert result.row_count == 2

    def test_insights(self):
        engine = AnalyticsEngine()
        records = [{"amount": 100}, {"amount": 200}, {"amount": 300}]
        insights = engine.generate_insights("sales", records)
        assert len(insights) > 0

    def test_anomalies(self):
        engine = AnalyticsEngine()
        records = [{"value": 10}] * 10 + [{"value": 100}]
        anomalies = engine.detect_anomalies("ds", records, "value", threshold=2.0)
        assert len(anomalies) > 0

    def test_dashboard(self):
        engine = AnalyticsEngine()
        dash = Dashboard(dashboard_id="D001", name="Sales Dashboard", widgets=[{"type": "chart"}])
        engine.create_dashboard(dash)
        assert engine.get_dashboard("D001") is dash


# ========== ML Tests ==========


class TestMLSubsystem:
    def test_create_model(self):
        engine = MLEngine()
        model = MLModel(model_id="M001", name="Sales Predictor", model_type=ModelType.REGRESSION)
        engine.create_model(model)
        assert engine.get_model("M001") is model

    def test_train_regression(self):
        engine = MLEngine()
        model = MLModel(model_id="M001", model_type=ModelType.REGRESSION)
        engine.create_model(model)
        records = [{"x": i, "y": i * 2 + 5} for i in range(100)]
        job = engine.train_model("M001", records, ["x"], "y")
        assert job.status == ModelStatus.TRAINED
        assert "mse" in model.metrics

    def test_train_classification(self):
        engine = MLEngine()
        model = MLModel(model_id="M001", model_type=ModelType.CLASSIFICATION)
        engine.create_model(model)
        records = [{"f1": i, "label": i % 2} for i in range(100)]
        job = engine.train_model("M001", records, ["f1"], "label")
        assert job.status == ModelStatus.TRAINED
        assert "accuracy" in model.metrics

    def test_predict(self):
        engine = MLEngine()
        model = MLModel(model_id="M001", model_type=ModelType.CLASSIFICATION, metrics={"accuracy": 0.9})
        engine.create_model(model)
        pred = engine.predict("M001", {"f1": 5})
        assert pred.confidence == 0.9

    def test_deploy(self):
        engine = MLEngine()
        model = MLModel(model_id="M001", model_type=ModelType.REGRESSION)
        engine.create_model(model)
        engine.train_model("M001", [{"x": 1, "y": 2}], ["x"], "y")
        assert engine.deploy_model("M001") is True
        assert model.status == ModelStatus.DEPLOYED

    def test_versions(self):
        engine = MLEngine()
        model = MLModel(model_id="M001", model_type=ModelType.REGRESSION)
        engine.create_model(model)
        engine.train_model("M001", [{"x": 1, "y": 2}], ["x"], "y")
        v = engine.save_version("M001")
        assert v is not None
        versions = engine.get_model_versions("M001")
        assert len(versions) == 1


# ========== Knowledge Graph Tests ==========


class TestKnowledgeGraphSubsystem:
    def test_add_entity(self):
        engine = KnowledgeGraphEngine()
        entity = Entity(entity_id="E001", name="Alice", entity_type=EntityType.PERSON)
        engine.add_entity(entity)
        assert engine.get_entity("E001") is entity

    def test_add_relation(self):
        engine = KnowledgeGraphEngine()
        e1 = Entity(entity_id="E001", name="Alice")
        e2 = Entity(entity_id="E002", name="Acme")
        engine.add_entity(e1)
        engine.add_entity(e2)
        rel = Relation(relation_id="R001", source_id="E001", target_id="E002", relation_type=RelationType.WORKS_FOR)
        engine.add_relation(rel)
        assert len(engine.get_entity_relations("E001")) == 1

    def test_neighbors(self):
        engine = KnowledgeGraphEngine()
        e1 = Entity(entity_id="E001", name="Alice")
        e2 = Entity(entity_id="E002", name="Acme")
        engine.add_entity(e1)
        engine.add_entity(e2)
        engine.add_relation(Relation(relation_id="R001", source_id="E001", target_id="E002"))
        neighbors = engine.get_neighbors("E001", max_depth=1)
        assert len(neighbors) == 1

    def test_find_path(self):
        engine = KnowledgeGraphEngine()
        e1 = Entity(entity_id="E001", name="Alice")
        e2 = Entity(entity_id="E002", name="Acme")
        e3 = Entity(entity_id="E003", name="ProductX")
        engine.add_entity(e1)
        engine.add_entity(e2)
        engine.add_entity(e3)
        engine.add_relation(Relation(relation_id="R001", source_id="E001", target_id="E002"))
        engine.add_relation(Relation(relation_id="R002", source_id="E002", target_id="E003"))
        path = engine.find_path("E001", "E003")
        assert path is not None
        assert len(path.entities) == 3

    def test_stats(self):
        engine = KnowledgeGraphEngine()
        engine.add_entity(Entity(entity_id="E001", entity_type=EntityType.PERSON))
        engine.add_entity(Entity(entity_id="E002", entity_type=EntityType.ORGANIZATION))
        engine.add_relation(Relation(relation_id="R001", source_id="E001", target_id="E002"))
        stats = engine.get_stats()
        assert stats["entities"] == 2
        assert stats["relations"] == 1


# ========== Support Class Tests ==========


class TestSupportClasses:
    def test_config(self):
        config = DataPlatformConfig()
        assert config.max_records_per_batch == 10000
        assert config.quality_threshold == 0.8

    def test_factory(self):
        src = DataPlatformFactory.create_source("Test DB", "database", "conn://localhost")
        assert src.name == "Test DB"
        rec = DataPlatformFactory.create_record("S001", "sales", {"amount": 100})
        assert rec.payload["amount"] == 100

    def test_metrics(self):
        m = DataPlatformMetrics()
        m.record_ingestion(10)
        m.record_quality_check(True)
        m.record_quality_check(False)
        stats = m.get_stats()
        assert stats["records_ingested"] == 10
        assert m.quality_rate == 50.0

    def test_logger(self):
        logger = DataPlatformLogger()
        logger.info("Test message", component="test")
        logger.error("Error message", component="test")
        assert logger.count == 2
        entries = logger.get_entries(DataLogLevel.ERROR)
        assert len(entries) == 1

    def test_security(self):
        sec = DataPlatformSecurity()
        sec.set_access("U001", "sales", DataAccessLevel.READ)
        assert sec.check_access("U001", "sales", DataAccessLevel.READ) is True
        assert sec.check_access("U001", "sales", DataAccessLevel.WRITE) is False
        sec.log_access("U001", "sales", "read")
        log = sec.get_audit_log(user_id="U001")
        assert len(log) == 1

    def test_context(self):
        ctx = DataPlatformContext()
        ctx.set("key1", "value1")
        assert ctx.get("key1") == "value1"
        assert ctx.has("key1") is True
        ctx.delete("key1")
        assert ctx.has("key1") is False

    def test_runtime(self):
        rt = DataPlatformRuntime()
        rt.start()
        assert rt.is_running is True
        rt.record_metric("records", 100)
        assert rt.get_metric("records") == 100
        rt.stop()
        assert rt.is_running is False
