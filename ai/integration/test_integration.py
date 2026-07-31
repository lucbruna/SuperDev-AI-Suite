"""Comprehensive tests for Integration Hub & API Ecosystem Engine (Volume 29)."""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# ── Core imports ──────────────────────────────────────────────────────────
# ── Adapters ──────────────────────────────────────────────────────────────
from integration.adapters.adapter_engine import AdapterConfig, AdapterEngine, AdapterType

# ── API Gateway ───────────────────────────────────────────────────────────
from integration.api_gateway.api_gateway_engine import APIGatewayEngine
from integration.api_gateway.api_gateway_engine import HttpMethod as GWHttpMethod
from integration.api_gateway.rate_limit import RateLimiter
from integration.api_gateway.versioning import VersionManager
from integration.authentication.api_keys import APIKeyManager
from integration.authentication.certificates import CertificateManager

# ── Authentication ────────────────────────────────────────────────────────
from integration.authentication.integration_auth import AuthType, IntegrationAuth
from integration.mapping.field_mapper import FieldMapper

# ── Mapping ───────────────────────────────────────────────────────────────
from integration.mapping.mapping_engine import MappingEngine
from integration.mapping.schema_mapper import SchemaMapper
from integration.mapping.transformation import TransformationEngine
from integration.mapping.validation import MappingValidator
from integration.monitoring.availability import AvailabilityMonitor
from integration.monitoring.errors import ErrorMonitor

# ── Monitoring ────────────────────────────────────────────────────────────
from integration.monitoring.integration_monitor import HealthStatus, IntegrationMonitor
from integration.monitoring.latency import LatencyMonitor
from integration.monitoring.reports import IntegrationReporter
from integration.queues.dead_letter import DeadLetterQueue
from integration.queues.message_queue import MessageQueue
from integration.queues.priority_queue import PriorityQueue

# ── Queues ────────────────────────────────────────────────────────────────
from integration.queues.queue_engine import QueueEngine, QueueState
from integration.queues.retry_queue import RetryQueue
from integration.synchronization.conflict_manager import ConflictManager
from integration.synchronization.data_sync import DataSync
from integration.synchronization.incremental_sync import IncrementalSync
from integration.synchronization.scheduler import SyncScheduler
from integration.webhooks.retry_manager import RetryManager

from integration.authentication.oauth import OAuthProvider
from integration.authentication.token_manager import IntegrationTokenManager

# ── Connectors ────────────────────────────────────────────────────────────
from integration.connectors.connector_engine import ConnectorConfig, ConnectorEngine, ConnectorState, ConnectorType
from integration.integration_config import ConfigFormat, IntegrationConfig
from integration.integration_context import IntegrationContext
from integration.integration_engine import IntegrationEngine
from integration.integration_events import EventType, IntegrationEvent, IntegrationEvents
from integration.integration_factory import IntegrationFactory
from integration.integration_interfaces import IntegrationInterfaces
from integration.integration_logger import IntegrationLogger
from integration.integration_manager import IntegrationManager
from integration.integration_metrics import IntegrationMetrics
from integration.integration_models import DataFormat, IntegrationModels
from integration.integration_protocols import IntegrationProtocols, ProtocolType
from integration.integration_registry import IntegrationRegistry
from integration.integration_runtime import IntegrationRuntime
from integration.integration_security import AuthMethod, IntegrationSecurity

# ── Synchronization ──────────────────────────────────────────────────────
from integration.synchronization.sync_engine import SyncDirection, SyncEngine, SyncStatus
from integration.webhooks.receiver import WebhookReceiver
from integration.webhooks.sender import WebhookSender
from integration.webhooks.validator import WebhookValidator

# ── Webhooks ──────────────────────────────────────────────────────────────
from integration.webhooks.webhook_engine import WebhookEngine, WebhookStatus

# ═══════════════════════════════════════════════════════════════════════════
# CORE TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestCoreModules(unittest.TestCase):
    def test_integration_engine_init(self):
        engine = IntegrationEngine()
        self.assertIsNotNone(engine)

    def test_integration_manager_init(self):
        mgr = IntegrationManager()
        self.assertIsNotNone(mgr)

    def test_integration_factory_init(self):
        f = IntegrationFactory()
        self.assertIsNotNone(f)

    def test_integration_registry_init(self):
        r = IntegrationRegistry()
        self.assertIsNotNone(r)

    def test_integration_runtime_init(self):
        rt = IntegrationRuntime()
        self.assertIsNotNone(rt)

    def test_integration_context_init(self):
        ctx = IntegrationContext()
        self.assertIsNotNone(ctx)

    def test_event_creation(self):
        event = IntegrationEvent(
            event_id="evt_1", event_type=EventType.INTEGRATION_CREATED, source="unit_test", data={"key": "value"}
        )
        self.assertEqual(event.event_type, EventType.INTEGRATION_CREATED)

    def test_event_bus_init(self):
        bus = IntegrationEvents()
        self.assertIsNotNone(bus)

    def test_metrics_init(self):
        m = IntegrationMetrics()
        self.assertIsNotNone(m)

    def test_logger_init(self):
        l = IntegrationLogger()
        self.assertIsNotNone(l)

    def test_security_init(self):
        s = IntegrationSecurity()
        self.assertIsNotNone(s)

    def test_models_init(self):
        m = IntegrationModels()
        self.assertIsNotNone(m)

    def test_interfaces_init(self):
        i = IntegrationInterfaces()
        self.assertIsNotNone(i)

    def test_protocols_init(self):
        p = IntegrationProtocols()
        self.assertIsNotNone(p)

    def test_config_init(self):
        c = IntegrationConfig()
        self.assertIsNotNone(c)

    def test_event_type_enum(self):
        self.assertIsNotNone(EventType)

    def test_auth_method_enum(self):
        self.assertIsNotNone(AuthMethod)

    def test_data_format_enum(self):
        self.assertIsNotNone(DataFormat)

    def test_protocol_type_enum(self):
        self.assertIsNotNone(ProtocolType)

    def test_config_format_enum(self):
        self.assertIsNotNone(ConfigFormat)


# ═══════════════════════════════════════════════════════════════════════════
# API GATEWAY TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestAPIGatewayEngine(unittest.TestCase):
    def setUp(self):
        self.engine = APIGatewayEngine()

    def test_add_route(self):
        route = self.engine.add_route("/api/v1/users", GWHttpMethod.GET, "users_service")
        self.assertIsNotNone(route)
        self.assertEqual(route.path, "/api/v1/users")

    def test_get_route(self):
        self.engine.add_route("/api/v1/orders", GWHttpMethod.POST, "orders_service")
        found = self.engine.get_route("/api/v1/orders", GWHttpMethod.POST)
        self.assertIsNotNone(found)

    def test_remove_route(self):
        route = self.engine.add_route("/api/v1/items", GWHttpMethod.DELETE, "items_service")
        result = self.engine.remove_route(route.route_id)
        self.assertTrue(result)

    def test_remove_nonexistent_route(self):
        result = self.engine.remove_route("nonexistent")
        self.assertFalse(result)

    def test_register_handler(self):
        route = self.engine.add_route("/api/v1/data", GWHttpMethod.GET, "data_service")

        def handler(req):
            return {"status": 200}

        self.engine.register_handler(route.route_id, handler)
        self.assertIn(route.route_id, self.engine.handlers)

    def test_add_middleware(self):
        def mw(req, next_fn):
            return next_fn(req)

        self.engine.add_middleware(mw)
        self.assertEqual(len(self.engine.middleware), 1)

    def test_http_method_enum(self):
        self.assertEqual(GWHttpMethod.GET.value, "GET")
        self.assertEqual(GWHttpMethod.POST.value, "POST")
        self.assertEqual(GWHttpMethod.PUT.value, "PUT")
        self.assertEqual(GWHttpMethod.DELETE.value, "DELETE")


class TestRateLimiter(unittest.TestCase):
    def setUp(self):
        self.limiter = RateLimiter()

    def test_set_config(self):
        config = self.limiter.set_config("api", max_requests=100, window_seconds=60)
        self.assertEqual(config.max_requests, 100)

    def test_check_allows_within_limit(self):
        self.limiter.set_config("test", max_requests=5, window_seconds=60)
        result = self.limiter.check("test")
        self.assertTrue(result.allowed)

    def test_check_blocks_over_limit(self):
        self.limiter.set_config("test", max_requests=2, window_seconds=60)
        self.limiter.check("test")
        self.limiter.check("test")
        result = self.limiter.check("test")
        self.assertFalse(result.allowed)

    def test_reset(self):
        self.limiter.set_config("test", max_requests=1, window_seconds=60)
        self.limiter.check("test")
        self.limiter.reset("test")
        result = self.limiter.check("test")
        self.assertTrue(result.allowed)

    def test_get_usage(self):
        self.limiter.set_config("test", max_requests=10, window_seconds=60)
        self.limiter.check("test")
        self.limiter.check("test")
        self.assertEqual(self.limiter.get_usage("test"), 2)


class TestVersionManager(unittest.TestCase):
    def setUp(self):
        self.vm = VersionManager()

    def test_register_version(self):
        v = self.vm.register_version("v1", base_path="/api/v1")
        self.assertEqual(v.version, "v1")

    def test_get_version(self):
        self.vm.register_version("v2")
        v = self.vm.get_version("v2")
        self.assertIsNotNone(v)

    def test_deprecate_version(self):
        self.vm.register_version("v1")
        result = self.vm.deprecate_version("v1")
        self.assertTrue(result)
        v = self.vm.get_version("v1")
        self.assertTrue(v.deprecated)

    def test_set_default(self):
        self.vm.register_version("v2")
        result = self.vm.set_default("v2")
        self.assertTrue(result)
        self.assertEqual(self.vm.default_version, "v2")

    def test_get_active(self):
        self.vm.register_version("v1")
        self.vm.register_version("v2")
        self.vm.deprecate_version("v1")
        active = self.vm.get_active()
        self.assertEqual(len(active), 1)

    def test_count(self):
        self.vm.register_version("v1")
        self.vm.register_version("v2")
        self.assertEqual(self.vm.count(), 2)


# ═══════════════════════════════════════════════════════════════════════════
# CONNECTORS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestConnectorEngine(unittest.TestCase):
    def setUp(self):
        self.engine = ConnectorEngine()

    def test_create_connector(self):
        config = ConnectorConfig(name="postgres", connector_type=ConnectorType.DATABASE, endpoint="localhost:5432")
        instance = self.engine.create_connector(config)
        self.assertIsNotNone(instance)
        self.assertEqual(instance.config.name, "postgres")
        self.assertEqual(instance.state, ConnectorState.DISCONNECTED)

    def test_connect_without_handler(self):
        config = ConnectorConfig(name="api", connector_type=ConnectorType.REST_API, endpoint="http://api.test")
        instance = self.engine.create_connector(config)
        result = self.engine.connect(instance.instance_id)
        self.assertTrue(result)
        self.assertEqual(instance.state, ConnectorState.CONNECTED)

    def test_connect_nonexistent(self):
        result = self.engine.connect("nonexistent")
        self.assertFalse(result)

    def test_connect_with_handler(self):
        config = ConnectorConfig(name="test", connector_type=ConnectorType.REST_API)
        instance = self.engine.create_connector(config)

        def handler(action, cfg):
            return None

        self.engine.register_handler(instance.instance_id, handler)
        result = self.engine.connect(instance.instance_id)
        self.assertTrue(result)

    def test_connect_with_failing_handler(self):
        config = ConnectorConfig(name="fail", connector_type=ConnectorType.REST_API)
        instance = self.engine.create_connector(config)

        def bad_handler(action, cfg):
            raise Exception("Connection refused")

        self.engine.register_handler(instance.instance_id, bad_handler)
        result = self.engine.connect(instance.instance_id)
        self.assertFalse(result)
        self.assertEqual(instance.state, ConnectorState.ERROR)
        self.assertEqual(instance.error_count, 1)

    def test_disconnect(self):
        config = ConnectorConfig(name="test", connector_type=ConnectorType.REST_API)
        instance = self.engine.create_connector(config)
        self.engine.connect(instance.instance_id)
        result = self.engine.disconnect(instance.instance_id)
        self.assertTrue(result)
        self.assertEqual(instance.state, ConnectorState.DISCONNECTED)

    def test_connector_type_enum(self):
        self.assertEqual(ConnectorType.REST_API.value, "rest_api")
        self.assertEqual(ConnectorType.DATABASE.value, "database")

    def test_connector_state_enum(self):
        self.assertEqual(ConnectorState.DISCONNECTED.value, "disconnected")
        self.assertEqual(ConnectorState.CONNECTED.value, "connected")


# ═══════════════════════════════════════════════════════════════════════════
# ADAPTERS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestAdapterEngine(unittest.TestCase):
    def setUp(self):
        self.engine = AdapterEngine()

    def test_register_adapter(self):
        config = AdapterConfig(
            name="json_to_xml", adapter_type=AdapterType.FORMAT, source_format="json", target_format="xml"
        )
        adapter_id = self.engine.register_adapter(config)
        self.assertIsNotNone(adapter_id)
        self.assertEqual(self.engine.count(), 1)

    def test_translate_without_handler(self):
        config = AdapterConfig(name="passthrough", adapter_type=AdapterType.DATA)
        adapter_id = self.engine.register_adapter(config)
        result = self.engine.translate(adapter_id, {"key": "value"})
        self.assertTrue(result.success)
        self.assertEqual(result.data, {"key": "value"})

    def test_translate_nonexistent_adapter(self):
        result = self.engine.translate("nonexistent", "data")
        self.assertFalse(result.success)

    def test_translate_with_handler(self):
        config = AdapterConfig(name="upper", adapter_type=AdapterType.FORMAT)
        adapter_id = self.engine.register_adapter(config)

        def handler(data, rules):
            return data.upper() if isinstance(data, str) else data

        self.engine.register_handler(adapter_id, handler)
        result = self.engine.translate(adapter_id, "hello")
        self.assertTrue(result.success)
        self.assertEqual(result.data, "HELLO")

    def test_translate_with_failing_handler(self):
        config = AdapterConfig(name="fail", adapter_type=AdapterType.CUSTOM)
        adapter_id = self.engine.register_adapter(config)

        def bad_handler(data, rules):
            raise ValueError("Bad data")

        self.engine.register_handler(adapter_id, bad_handler)
        result = self.engine.translate(adapter_id, "test")
        self.assertFalse(result.success)
        self.assertIn("Bad data", result.error)

    def test_get_adapter(self):
        config = AdapterConfig(name="test", adapter_type=AdapterType.PROTOCOL)
        adapter_id = self.engine.register_adapter(config)
        found = self.engine.get_adapter(adapter_id)
        self.assertIsNotNone(found)

    def test_list_adapters(self):
        self.engine.register_adapter(AdapterConfig(name="a", adapter_type=AdapterType.FORMAT))
        self.engine.register_adapter(AdapterConfig(name="b", adapter_type=AdapterType.PROTOCOL))
        self.assertEqual(len(self.engine.list_adapters()), 2)

    def test_translation_log(self):
        config = AdapterConfig(name="log_test", adapter_type=AdapterType.DATA)
        adapter_id = self.engine.register_adapter(config)
        self.engine.translate(adapter_id, "data1")
        self.engine.translate(adapter_id, "data2")
        self.assertEqual(len(self.engine.get_log()), 2)


# ═══════════════════════════════════════════════════════════════════════════
# AUTHENTICATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestIntegrationAuth(unittest.TestCase):
    def setUp(self):
        self.auth = IntegrationAuth()

    def test_create_credential(self):
        cred = self.auth.create_credential("integration_1", AuthType.API_KEY, secret="my_secret_key")
        self.assertIsNotNone(cred)
        self.assertEqual(cred.integration_id, "integration_1")

    def test_validate_credential(self):
        cred = self.auth.create_credential("int_1", AuthType.API_KEY, secret="key123")
        self.assertTrue(self.auth.validate_credential(cred.credential_id, secret="key123"))

    def test_validate_credential_wrong_secret(self):
        cred = self.auth.create_credential("int_1", AuthType.API_KEY, secret="key123")
        self.assertFalse(self.auth.validate_credential(cred.credential_id, secret="wrong"))

    def test_revoke_credential(self):
        cred = self.auth.create_credential("int_1", AuthType.OAUTH2)
        self.assertTrue(self.auth.revoke_credential(cred.credential_id))
        self.assertFalse(self.auth.validate_credential(cred.credential_id))

    def test_authenticate(self):
        self.auth.create_credential("int_1", AuthType.API_KEY)
        token = self.auth.authenticate("int_1", AuthType.API_KEY, {})
        self.assertIsNotNone(token)
        self.assertTrue(self.auth.validate_session(token))

    def test_authenticate_no_credential(self):
        token = self.auth.authenticate("nonexistent", AuthType.API_KEY, {})
        self.assertIsNone(token)

    def test_invalidate_session(self):
        self.auth.create_credential("int_1", AuthType.API_KEY)
        token = self.auth.authenticate("int_1", AuthType.API_KEY, {})
        self.assertTrue(self.auth.invalidate_session(token))
        self.assertFalse(self.auth.validate_session(token))

    def test_get_credentials(self):
        self.auth.create_credential("int_1", AuthType.API_KEY)
        self.auth.create_credential("int_1", AuthType.OAUTH2)
        self.auth.create_credential("int_2", AuthType.BASIC)
        self.assertEqual(len(self.auth.get_credentials("int_1")), 2)

    def test_auth_type_enum(self):
        self.assertEqual(AuthType.API_KEY.value, "api_key")
        self.assertEqual(AuthType.OAUTH2.value, "oauth2")


class TestOAuthProvider(unittest.TestCase):
    def test_init(self):
        p = OAuthProvider()
        self.assertIsNotNone(p)


class TestAPIKeyManager(unittest.TestCase):
    def test_init(self):
        m = APIKeyManager()
        self.assertIsNotNone(m)


class TestCertificateManager(unittest.TestCase):
    def test_init(self):
        m = CertificateManager()
        self.assertIsNotNone(m)


class TestIntegrationTokenManager(unittest.TestCase):
    def test_init(self):
        m = IntegrationTokenManager()
        self.assertIsNotNone(m)


# ═══════════════════════════════════════════════════════════════════════════
# WEBHOOKS TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestWebhookEngine(unittest.TestCase):
    def setUp(self):
        self.engine = WebhookEngine()

    def test_register_webhook(self):
        wh = self.engine.register_webhook("github", "https://github.com/hook", events=["push", "pull_request"])
        self.assertIsNotNone(wh)
        self.assertEqual(wh.name, "github")
        self.assertEqual(wh.status, WebhookStatus.ACTIVE)

    def test_unregister_webhook(self):
        wh = self.engine.register_webhook("test", "https://test.com/hook")
        self.assertTrue(self.engine.unregister_webhook(wh.webhook_id))

    def test_unregister_nonexistent(self):
        self.assertFalse(self.engine.unregister_webhook("nonexistent"))

    def test_trigger_event(self):
        self.engine.register_webhook("listener", "https://listener.com/hook", events=["order.created"])
        events = self.engine.trigger_event("order.created", {"order_id": 123})
        self.assertEqual(len(events), 1)

    def test_trigger_wildcard(self):
        self.engine.register_webhook("all", "https://all.com/hook", events=["*"])
        events = self.engine.trigger_event("anything.happens", {})
        self.assertEqual(len(events), 1)

    def test_trigger_no_match(self):
        self.engine.register_webhook("specific", "https://spec.com/hook", events=["push"])
        events = self.engine.trigger_event("pull_request", {})
        self.assertEqual(len(events), 0)

    def test_handle_response(self):
        self.engine.register_webhook("test", "https://test.com/hook")
        events = self.engine.trigger_event("test.event", {})
        result = self.engine.handle_response(events[0].event_id, "delivered", 200)
        self.assertTrue(result)

    def test_webhook_status_enum(self):
        self.assertEqual(WebhookStatus.ACTIVE.value, "active")
        self.assertEqual(WebhookStatus.INACTIVE.value, "inactive")


class TestWebhookSubModules(unittest.TestCase):
    def test_receiver_init(self):
        self.assertIsNotNone(WebhookReceiver())

    def test_sender_init(self):
        self.assertIsNotNone(WebhookSender())

    def test_validator_init(self):
        self.assertIsNotNone(WebhookValidator())

    def test_retry_manager_init(self):
        self.assertIsNotNone(RetryManager())


# ═══════════════════════════════════════════════════════════════════════════
# SYNCHRONIZATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSyncEngine(unittest.TestCase):
    def setUp(self):
        self.engine = SyncEngine()

    def test_create_job(self):
        job = self.engine.create_job("sync_users", "db_source", "db_target")
        self.assertIsNotNone(job)
        self.assertEqual(job.status, SyncStatus.IDLE)

    def test_execute_sync(self):
        job = self.engine.create_job("sync_orders", "api_1", "api_2")
        result = self.engine.execute_sync(job.job_id, data=[1, 2, 3])
        self.assertTrue(result["success"])
        self.assertEqual(result["records_synced"], 3)
        self.assertEqual(job.status, SyncStatus.COMPLETED)

    def test_execute_sync_nonexistent(self):
        result = self.engine.execute_sync("nonexistent")
        self.assertFalse(result["success"])

    def test_schedule_job(self):
        job = self.engine.create_job("sched", "s", "t")
        self.engine.schedule_job(job.job_id, interval_seconds=1800)
        self.assertIn(job.job_id, self.engine.schedules)

    def test_list_jobs(self):
        self.engine.create_job("j1", "s1", "t1")
        self.engine.create_job("j2", "s2", "t2")
        self.assertEqual(len(self.engine.list_jobs()), 2)

    def test_sync_log(self):
        job = self.engine.create_job("log", "s", "t")
        self.engine.execute_sync(job.job_id, data="x")
        self.assertEqual(len(self.engine.get_log()), 1)

    def test_sync_direction_enum(self):
        self.assertEqual(SyncDirection.BIDIRECTIONAL.value, "bidirectional")

    def test_sync_status_enum(self):
        self.assertEqual(SyncStatus.IDLE.value, "idle")
        self.assertEqual(SyncStatus.COMPLETED.value, "completed")


class TestSyncSubModules(unittest.TestCase):
    def test_data_sync_init(self):
        self.assertIsNotNone(DataSync())

    def test_conflict_manager_init(self):
        self.assertIsNotNone(ConflictManager())

    def test_scheduler_init(self):
        self.assertIsNotNone(SyncScheduler())

    def test_incremental_sync_init(self):
        self.assertIsNotNone(IncrementalSync())


# ═══════════════════════════════════════════════════════════════════════════
# MAPPING TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestMappingEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MappingEngine()

    def test_create_mapping(self):
        config = self.engine.create_mapping("user_to_contact", "user_schema", "contact_schema")
        self.assertIsNotNone(config)
        self.assertEqual(config.name, "user_to_contact")

    def test_add_rule(self):
        self.engine.create_mapping("m1", "src", "tgt")
        rule = self.engine.add_rule("m1", "first_name", "given_name")
        self.assertIsNotNone(rule)

    def test_add_rule_nonexistent(self):
        self.assertIsNone(self.engine.add_rule("nonexistent", "a", "b"))

    def test_map_data(self):
        self.engine.create_mapping("m1", "src", "tgt")
        self.engine.add_rule("m1", "name", "full_name")
        self.engine.add_rule("m1", "age", "years")
        result = self.engine.map_data("m1", {"name": "Alice", "age": 30})
        self.assertEqual(result["full_name"], "Alice")
        self.assertEqual(result["years"], 30)

    def test_map_data_default(self):
        self.engine.create_mapping("m1", "src", "tgt")
        self.engine.add_rule("m1", "missing", "output", default_value="N/A")
        result = self.engine.map_data("m1", {})
        self.assertEqual(result["output"], "N/A")

    def test_transform_upper(self):
        self.engine.create_mapping("m1", "src", "tgt")
        self.engine.add_rule("m1", "name", "NAME", transform="upper")
        result = self.engine.map_data("m1", {"name": "alice"})
        self.assertEqual(result["NAME"], "ALICE")

    def test_transform_lower(self):
        self.engine.create_mapping("m1", "src", "tgt")
        self.engine.add_rule("m1", "name", "name_lower", transform="lower")
        result = self.engine.map_data("m1", {"name": "ALICE"})
        self.assertEqual(result["name_lower"], "alice")

    def test_transform_str(self):
        self.engine.create_mapping("m1", "src", "tgt")
        self.engine.add_rule("m1", "num", "num_str", transform="str")
        result = self.engine.map_data("m1", {"num": 42})
        self.assertEqual(result["num_str"], "42")

    def test_transform_int(self):
        self.engine.create_mapping("m1", "src", "tgt")
        self.engine.add_rule("m1", "val", "val_int", transform="int")
        result = self.engine.map_data("m1", {"val": "123"})
        self.assertEqual(result["val_int"], 123)

    def test_map_nonexistent(self):
        result = self.engine.map_data("nonexistent", {"a": 1})
        self.assertEqual(result, {"a": 1})

    def test_list_mappings(self):
        self.engine.create_mapping("m1", "s", "t")
        self.engine.create_mapping("m2", "s", "t")
        self.assertEqual(len(self.engine.list_mappings()), 2)

    def test_count(self):
        self.engine.create_mapping("m1", "s", "t")
        self.assertEqual(self.engine.count(), 1)


class TestMappingSubModules(unittest.TestCase):
    def test_schema_mapper_init(self):
        self.assertIsNotNone(SchemaMapper())

    def test_field_mapper_init(self):
        self.assertIsNotNone(FieldMapper())

    def test_transformation_engine_init(self):
        self.assertIsNotNone(TransformationEngine())

    def test_mapping_validator_init(self):
        self.assertIsNotNone(MappingValidator())


# ═══════════════════════════════════════════════════════════════════════════
# QUEUES TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestQueueEngine(unittest.TestCase):
    def setUp(self):
        self.engine = QueueEngine()

    def test_create_queue(self):
        self.engine.create_queue("orders")
        self.assertIn("orders", self.engine.queues)
        self.assertEqual(self.engine.queue_states["orders"], QueueState.ACTIVE)

    def test_enqueue_dequeue(self):
        msg = self.engine.enqueue("tasks", {"action": "process"})
        self.assertIsNotNone(msg)
        dequeued = self.engine.dequeue("tasks")
        self.assertIsNotNone(dequeued)
        self.assertEqual(dequeued.message_id, msg.message_id)

    def test_dequeue_empty(self):
        self.assertIsNone(self.engine.dequeue("empty_queue"))

    def test_enqueue_auto_creates(self):
        self.engine.enqueue("auto", "data")
        self.assertIn("auto", self.engine.queues)

    def test_complete_message(self):
        msg = self.engine.enqueue("q", "data")
        self.engine.dequeue("q")
        self.assertTrue(self.engine.complete(msg.message_id))
        self.assertEqual(msg.state, "completed")

    def test_fail_retry(self):
        msg = self.engine.enqueue("q", "data")
        self.engine.dequeue("q")
        self.assertTrue(self.engine.fail(msg.message_id, "timeout"))
        self.assertEqual(msg.attempts, 1)
        self.assertEqual(msg.state, "pending")

    def test_fail_dead_letter(self):
        msg = self.engine.enqueue("q", "data")
        msg.max_retries = 2
        self.engine.dequeue("q")
        self.engine.fail(msg.message_id, "err1")
        self.engine.dequeue("q")
        self.engine.fail(msg.message_id, "err2")
        self.assertEqual(msg.state, "dead_letter")

    def test_queue_state_enum(self):
        self.assertEqual(QueueState.ACTIVE.value, "active")
        self.assertEqual(QueueState.PAUSED.value, "paused")


class TestQueueSubModules(unittest.TestCase):
    def test_message_queue_init(self):
        self.assertIsNotNone(MessageQueue())

    def test_priority_queue_init(self):
        self.assertIsNotNone(PriorityQueue())

    def test_retry_queue_init(self):
        self.assertIsNotNone(RetryQueue())

    def test_dead_letter_queue_init(self):
        self.assertIsNotNone(DeadLetterQueue())


# ═══════════════════════════════════════════════════════════════════════════
# MONITORING TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestIntegrationMonitor(unittest.TestCase):
    def setUp(self):
        self.monitor = IntegrationMonitor()

    def test_check_health(self):
        check = self.monitor.check_health("int_1", HealthStatus.HEALTHY, "All good", 50.0)
        self.assertIsNotNone(check)
        self.assertEqual(check.status, HealthStatus.HEALTHY)

    def test_get_status(self):
        self.monitor.check_health("int_1", HealthStatus.HEALTHY)
        status = self.monitor.get_status("int_1")
        self.assertIsNotNone(status)
        self.assertTrue(status.is_online)

    def test_health_history(self):
        self.monitor.check_health("int_1", HealthStatus.HEALTHY)
        self.monitor.check_health("int_1", HealthStatus.DEGRADED)
        self.assertEqual(len(self.monitor.get_health_history("int_1")), 2)

    def test_alert(self):
        self.monitor.alert("int_1", "High latency", "warning")
        alerts = self.monitor.get_alerts("int_1")
        self.assertEqual(len(alerts), 1)

    def test_get_all_alerts(self):
        self.monitor.alert("int_1", "msg1")
        self.monitor.alert("int_2", "msg2")
        self.assertEqual(len(self.monitor.get_alerts()), 2)

    def test_uptime(self):
        self.monitor.check_health("int_1", HealthStatus.HEALTHY)
        self.monitor.check_health("int_1", HealthStatus.HEALTHY)
        self.monitor.check_health("int_1", HealthStatus.DEGRADED)
        uptime = self.monitor.get_uptime("int_1")
        self.assertAlmostEqual(uptime, 66.67, places=1)

    def test_uptime_no_checks(self):
        self.assertEqual(self.monitor.get_uptime("nonexistent"), 100.0)

    def test_avg_latency(self):
        self.monitor.check_health("int_1", HealthStatus.HEALTHY, latency_ms=100)
        self.monitor.check_health("int_1", HealthStatus.HEALTHY, latency_ms=200)
        self.assertEqual(self.monitor.get_avg_latency("int_1"), 150.0)

    def test_health_status_enum(self):
        self.assertEqual(HealthStatus.HEALTHY.value, "healthy")
        self.assertEqual(HealthStatus.DEGRADED.value, "degraded")


class TestMonitoringSubModules(unittest.TestCase):
    def test_latency_monitor_init(self):
        self.assertIsNotNone(LatencyMonitor())

    def test_error_monitor_init(self):
        self.assertIsNotNone(ErrorMonitor())

    def test_availability_monitor_init(self):
        self.assertIsNotNone(AvailabilityMonitor())

    def test_integration_reporter_init(self):
        self.assertIsNotNone(IntegrationReporter())


# ═══════════════════════════════════════════════════════════════════════════
# SUBSYSTEM IMPORT TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestSubsystemImports(unittest.TestCase):
    def test_api_gateway_imports(self):
        from integration.api_gateway import (
            APIGatewayEngine,
            RateLimiter,
            RequestHandler,
            ResponseManager,
            RouteManager,
            VersionManager,
        )

        self.assertTrue(
            all([APIGatewayEngine, RouteManager, RequestHandler, ResponseManager, RateLimiter, VersionManager])
        )

    def test_connectors_imports(self):
        from integration.connectors import (
            ConnectorEngine,
            ConnectorLoader,
            ConnectorManager,
            ConnectorRegistry,
            ConnectorValidator,
        )

        self.assertTrue(
            all([ConnectorEngine, ConnectorManager, ConnectorRegistry, ConnectorLoader, ConnectorValidator])
        )

    def test_adapters_imports(self):
        from integration.adapters import AdapterEngine, AdapterManager, FormatAdapter, LegacyAdapter, ProtocolAdapter

        self.assertTrue(all([AdapterEngine, AdapterManager, ProtocolAdapter, FormatAdapter, LegacyAdapter]))

    def test_authentication_imports(self):
        from integration.authentication import (
            APIKeyManager,
            CertificateManager,
            IntegrationAuth,
            IntegrationTokenManager,
            OAuthProvider,
        )

        self.assertTrue(
            all([IntegrationAuth, OAuthProvider, APIKeyManager, CertificateManager, IntegrationTokenManager])
        )

    def test_webhooks_imports(self):
        from integration.webhooks import RetryManager, WebhookEngine, WebhookReceiver, WebhookSender, WebhookValidator

        self.assertTrue(all([WebhookEngine, WebhookReceiver, WebhookSender, WebhookValidator, RetryManager]))

    def test_synchronization_imports(self):
        from integration.synchronization import ConflictManager, DataSync, IncrementalSync, SyncEngine, SyncScheduler

        self.assertTrue(all([SyncEngine, DataSync, ConflictManager, SyncScheduler, IncrementalSync]))

    def test_mapping_imports(self):
        from integration.mapping import FieldMapper, MappingEngine, MappingValidator, SchemaMapper, TransformationEngine

        self.assertTrue(all([MappingEngine, SchemaMapper, FieldMapper, TransformationEngine, MappingValidator]))

    def test_queues_imports(self):
        from integration.queues import DeadLetterQueue, MessageQueue, PriorityQueue, QueueEngine, RetryQueue

        self.assertTrue(all([QueueEngine, MessageQueue, PriorityQueue, RetryQueue, DeadLetterQueue]))

    def test_monitoring_imports(self):
        from integration.monitoring import (
            AvailabilityMonitor,
            ErrorMonitor,
            IntegrationMonitor,
            IntegrationReporter,
            LatencyMonitor,
        )

        self.assertTrue(
            all([IntegrationMonitor, LatencyMonitor, ErrorMonitor, AvailabilityMonitor, IntegrationReporter])
        )


# ═══════════════════════════════════════════════════════════════════════════
# CROSS-SUBSYSTEM INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════


class TestCrossSubsystemIntegration(unittest.TestCase):
    def test_gateway_rate_limit_and_auth(self):
        gw = APIGatewayEngine()
        limiter = RateLimiter()
        auth = IntegrationAuth()

        limiter.set_config("api", max_requests=5, window_seconds=60)
        cred = auth.create_credential("svc_1", AuthType.API_KEY, secret="key123")
        gw.add_route("/api/data", GWHttpMethod.GET, "data_service")

        self.assertTrue(limiter.check("api").allowed)
        self.assertTrue(auth.validate_credential(cred.credential_id, "key123"))
        self.assertIsNotNone(gw.get_route("/api/data", GWHttpMethod.GET))

    def test_connector_adapter_pipeline(self):
        engine = ConnectorEngine()
        adapter = AdapterEngine()

        config = ConnectorConfig(name="legacy_db", connector_type=ConnectorType.DATABASE)
        instance = engine.create_connector(config)
        engine.connect(instance.instance_id)

        adapter_config = AdapterConfig(
            name="db_to_json", adapter_type=AdapterType.FORMAT, source_format="csv", target_format="json"
        )
        adapter_id = adapter.register_adapter(adapter_config)
        result = adapter.translate(adapter_id, "col1,col2\nval1,val2")
        self.assertTrue(result.success)

    def test_webhook_sync_mapping_pipeline(self):
        webhook_engine = WebhookEngine()
        sync_engine = SyncEngine()
        mapping_engine = MappingEngine()

        webhook_engine.register_webhook("sync_trigger", "https://sync.com/hook", events=["data.changed"])
        mapping_engine.create_mapping("dt", "source", "target")
        mapping_engine.add_rule("dt", "id", "record_id")
        mapping_engine.add_rule("dt", "value", "data_value", transform="upper")
        job = sync_engine.create_job("ws", "webhook_source", "target_db")

        events = webhook_engine.trigger_event("data.changed", {"id": 1, "value": "test"})
        self.assertEqual(len(events), 1)

        mapped = mapping_engine.map_data("dt", {"id": 42, "value": "hello"})
        self.assertEqual(mapped["record_id"], 42)
        self.assertEqual(mapped["data_value"], "HELLO")

        result = sync_engine.execute_sync(job.job_id, data=mapped)
        self.assertTrue(result["success"])

    def test_queue_monitor_pipeline(self):
        qe = QueueEngine()
        mon = IntegrationMonitor()

        qe.create_queue("events")
        qe.enqueue("events", {"type": "alert"})
        check = mon.check_health("queue_service", HealthStatus.HEALTHY, latency_ms=25.0)
        self.assertEqual(check.status, HealthStatus.HEALTHY)

        dequeued = qe.dequeue("events")
        self.assertIsNotNone(dequeued)
        qe.complete(dequeued.message_id)
        self.assertEqual(mon.get_uptime("queue_service"), 100.0)

    def test_full_lifecycle(self):
        gw = APIGatewayEngine()
        auth = IntegrationAuth()
        connector = ConnectorEngine()
        mapping = MappingEngine()
        sync = SyncEngine()
        mon = IntegrationMonitor()

        auth.create_credential("ext_api", AuthType.OAUTH2)
        token = auth.authenticate("ext_api", AuthType.OAUTH2, {})
        route = gw.add_route("/api/v1/sync", GWHttpMethod.POST, "sync_service")

        config = ConnectorConfig(
            name="ext_api", connector_type=ConnectorType.REST_API, endpoint="https://api.external.com"
        )
        instance = connector.create_connector(config)
        connector.connect(instance.instance_id)

        mapping.create_mapping("e2i", "external", "internal")
        mapping.add_rule("e2i", "ext_id", "int_id")
        mapping.add_rule("e2i", "ext_name", "int_name", transform="upper")
        mapped = mapping.map_data("e2i", {"ext_id": 100, "ext_name": "product"})

        job = sync.create_job("full_sync", "external", "internal")
        result = sync.execute_sync(job.job_id, data=mapped)
        mon.check_health("ext_api", HealthStatus.HEALTHY, latency_ms=120.0)

        self.assertIsNotNone(token)
        self.assertIsNotNone(route)
        self.assertEqual(instance.state, ConnectorState.CONNECTED)
        self.assertEqual(mapped["int_name"], "PRODUCT")
        self.assertTrue(result["success"])
        self.assertTrue(mon.get_status("ext_api").is_online)


# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    unittest.main(verbosity=2)
