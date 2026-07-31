"""Comprehensive tests for Mobile Platform & Edge AI Engine (Volume 30)."""
import sys
import os
import unittest
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# ── Core imports ──────────────────────────────────────────────────────────
from mobile_edge.mobile_engine import MobileEngine, PlatformType, MobileState
from mobile_edge.edge_engine import EdgeEngine, ModelStatus, AcceleratorType
from mobile_edge.device_manager import DeviceManager, DeviceCategory, DeviceHealth
from mobile_edge.mobile_security import MobileSecurityManager, SecurityLevel, ThreatType
from mobile_edge.mobile_config import MobileConfig, ConfigScope
from mobile_edge.mobile_events import MobileEventBus, MobileEventType
from mobile_edge.mobile_metrics import MobileMetrics
from mobile_edge.mobile_logger import MobileLogger, LogLevel
from mobile_edge.mobile_models import SyncStrategy, ConnectionType, BatteryMode

# ── Edge Runtime ──────────────────────────────────────────────────────────
from mobile_edge.edge_runtime.edge_runtime_engine import EdgeRuntimeEngine, RuntimeState
from mobile_edge.edge_runtime.local_model import LocalModelManager, LocalModelStatus
from mobile_edge.edge_runtime.inference import InferenceEngine, InferenceRequest
from mobile_edge.edge_runtime.model_manager import EdgeModelManager, ModelLifecycle
from mobile_edge.edge_runtime.resource_manager import EdgeResourceManager, ResourceSnapshot
from mobile_edge.edge_runtime.accelerator import AcceleratorManager, AcceleratorStatus

# ── Offline ───────────────────────────────────────────────────────────────
from mobile_edge.offline.offline_engine import OfflineEngine, OfflineMode
from mobile_edge.offline.cache_manager import CacheManager, CacheEntry
from mobile_edge.offline.local_database import LocalDatabase, LocalRecord
from mobile_edge.offline.queue_manager import OfflineQueueManager, QueuePriority, QueueItemStatus
from mobile_edge.offline.sync_queue import SyncQueue, SyncItemStatus

# ── Synchronization ──────────────────────────────────────────────────────
from mobile_edge.synchronization.sync_engine import MobileSyncEngine, SyncDirection, SyncState
from mobile_edge.synchronization.conflict_resolution import ConflictResolver, ConflictStrategy
from mobile_edge.synchronization.data_merge import DataMerger
from mobile_edge.synchronization.cloud_sync import CloudSyncManager, CloudSyncStatus

# ── Devices ───────────────────────────────────────────────────────────────
from mobile_edge.devices.device_engine import DeviceEngine, DeviceStatus
from mobile_edge.devices.device_registry import DeviceRegistry
from mobile_edge.devices.device_health import DeviceHealthMonitor, HealthLevel
from mobile_edge.devices.remote_control import RemoteControlManager, RemoteCommand, CommandStatus
from mobile_edge.devices.inventory import DeviceInventory

# ── Notifications ────────────────────────────────────────────────────────
from mobile_edge.notifications.notification_engine import NotificationEngine, NotificationType, NotificationPriority
from mobile_edge.notifications.push_manager import PushManager
from mobile_edge.notifications.alert_rules import AlertRuleManager, AlertCondition
from mobile_edge.notifications.templates import TemplateManager

# ── Biometrics ───────────────────────────────────────────────────────────
from mobile_edge.biometrics.biometric_engine import BiometricEngine, BiometricType, AuthResult
from mobile_edge.biometrics.fingerprint import FingerprintManager
from mobile_edge.biometrics.face import FaceRecognitionManager
from mobile_edge.biometrics.voice import VoiceRecognitionManager


# ═══════════════════════════════════════════════════════════════════════════
# CORE TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestCoreModules(unittest.TestCase):
    def test_mobile_engine(self):
        e = MobileEngine()
        self.assertIsNotNone(e)

    def test_edge_engine(self):
        e = EdgeEngine()
        self.assertIsNotNone(e)

    def test_device_manager(self):
        e = DeviceManager()
        self.assertIsNotNone(e)

    def test_mobile_security(self):
        e = MobileSecurityManager()
        self.assertIsNotNone(e)

    def test_mobile_config(self):
        e = MobileConfig()
        self.assertIsNotNone(e)

    def test_mobile_events(self):
        e = MobileEventBus()
        self.assertIsNotNone(e)

    def test_mobile_metrics(self):
        e = MobileMetrics()
        self.assertIsNotNone(e)

    def test_mobile_logger(self):
        e = MobileLogger()
        self.assertIsNotNone(e)

    def test_platform_type_enum(self):
        self.assertEqual(PlatformType.ANDROID.value, "android")
        self.assertEqual(PlatformType.IOS.value, "ios")

    def test_mobile_state_enum(self):
        self.assertEqual(MobileState.ONLINE.value, "online")
        self.assertEqual(MobileState.OFFLINE.value, "offline")

    def test_model_status_enum(self):
        self.assertEqual(ModelStatus.LOADED.value, "loaded")

    def test_sync_strategy_enum(self):
        self.assertEqual(SyncStrategy.FULL.value, "full")

    def test_connection_type_enum(self):
        self.assertEqual(ConnectionType.WIFI.value, "wifi")

    def test_battery_mode_enum(self):
        self.assertEqual(BatteryMode.NORMAL.value, "normal")


class TestMobileEngine(unittest.TestCase):
    def setUp(self):
        self.engine = MobileEngine()

    def test_register_device(self):
        device = self.engine.register_device("Pixel 8", PlatformType.ANDROID, "14")
        self.assertIsNotNone(device)
        self.assertEqual(device.name, "Pixel 8")

    def test_get_device(self):
        device = self.engine.register_device("iPhone 15", PlatformType.IOS)
        found = self.engine.get_device(device.device_id)
        self.assertIsNotNone(found)

    def test_update_state(self):
        device = self.engine.register_device("Test", PlatformType.ANDROID)
        self.assertTrue(self.engine.update_state(device.device_id, MobileState.OFFLINE))
        self.assertEqual(device.state, MobileState.OFFLINE)

    def test_list_devices(self):
        self.engine.register_device("A", PlatformType.ANDROID)
        self.engine.register_device("B", PlatformType.IOS)
        self.assertEqual(len(self.engine.list_devices()), 2)

    def test_list_by_platform(self):
        self.engine.register_device("A", PlatformType.ANDROID)
        self.engine.register_device("B", PlatformType.IOS)
        android = self.engine.list_devices(platform=PlatformType.ANDROID)
        self.assertEqual(len(android), 1)

    def test_get_online_devices(self):
        d1 = self.engine.register_device("A", PlatformType.ANDROID)
        d2 = self.engine.register_device("B", PlatformType.IOS)
        self.engine.update_state(d2.device_id, MobileState.OFFLINE)
        online = self.engine.get_online_devices()
        self.assertEqual(len(online), 1)

    def test_session(self):
        device = self.engine.register_device("Test", PlatformType.ANDROID)
        session_id = self.engine.start_session(device.device_id)
        self.assertIsNotNone(session_id)
        self.assertTrue(self.engine.end_session(session_id))

    def test_count(self):
        self.engine.register_device("A", PlatformType.ANDROID)
        self.assertEqual(self.engine.count(), 1)


class TestEdgeEngine(unittest.TestCase):
    def setUp(self):
        self.engine = EdgeEngine()

    def test_register_model(self):
        model = self.engine.register_model("nlp", "2.0", 100.0)
        self.assertIsNotNone(model)
        self.assertEqual(model.name, "nlp")

    def test_load_model(self):
        model = self.engine.register_model("img", "1.0")
        self.assertTrue(self.engine.load_model(model.model_id))
        self.assertEqual(model.status, ModelStatus.LOADED)

    def test_load_nonexistent(self):
        self.assertFalse(self.engine.load_model("nonexistent"))

    def test_unload_model(self):
        model = self.engine.register_model("test", "1.0")
        self.engine.load_model(model.model_id)
        self.assertTrue(self.engine.unload_model(model.model_id))

    def test_infer(self):
        model = self.engine.register_model("test", "1.0")
        self.engine.load_model(model.model_id)
        result = self.engine.infer(model.model_id, "input")
        self.assertIsNotNone(result)

    def test_infer_unloaded(self):
        model = self.engine.register_model("test", "1.0")
        result = self.engine.infer(model.model_id, "input")
        self.assertIsNone(result)

    def test_list_models(self):
        self.engine.register_model("a", "1.0")
        self.engine.register_model("b", "1.0")
        self.assertEqual(len(self.engine.list_models()), 2)

    def test_get_loaded(self):
        m1 = self.engine.register_model("a", "1.0")
        m2 = self.engine.register_model("b", "1.0")
        self.engine.load_model(m1.model_id)
        loaded = self.engine.get_loaded_models()
        self.assertEqual(len(loaded), 1)


class TestDeviceManager(unittest.TestCase):
    def setUp(self):
        self.dm = DeviceManager()

    def test_register_device(self):
        device = self.dm.register_device("Pixel", DeviceCategory.SMARTPHONE)
        self.assertIsNotNone(device)

    def test_update_health(self):
        device = self.dm.register_device("Pixel", DeviceCategory.SMARTPHONE)
        self.assertTrue(self.dm.update_health(device.device_id, DeviceHealth.WARNING))
        self.assertEqual(device.health, DeviceHealth.WARNING)

    def test_groups(self):
        self.dm.create_group("mobile")
        device = self.dm.register_device("A", DeviceCategory.SMARTPHONE)
        self.assertTrue(self.dm.add_to_group("mobile", device.device_id))
        devices = self.dm.get_group_devices("mobile")
        self.assertEqual(len(devices), 1)

    def test_search(self):
        self.dm.register_device("Pixel 8", DeviceCategory.SMARTPHONE, tags=["google"])
        results = self.dm.search_devices("pixel")
        self.assertEqual(len(results), 1)

    def test_health_history(self):
        device = self.dm.register_device("Test", DeviceCategory.TABLET)
        self.dm.update_health(device.device_id, DeviceHealth.WARNING, "Battery low")
        history = self.dm.get_health_history(device.device_id)
        self.assertEqual(len(history), 1)


class TestMobileSecurity(unittest.TestCase):
    def setUp(self):
        self.sec = MobileSecurityManager()

    def test_create_policy(self):
        policy = self.sec.create_policy("high_security", SecurityLevel.HIGH)
        self.assertIsNotNone(policy)
        self.assertEqual(policy.level, SecurityLevel.HIGH)

    def test_register_device(self):
        sec = self.sec.register_device_security("dev_1")
        self.assertIsNotNone(sec)

    def test_scan_device(self):
        self.sec.register_device_security("dev_1")
        result = self.sec.scan_device("dev_1")
        self.assertEqual(result, ThreatType.NONE)

    def test_lock_device(self):
        self.sec.register_device_security("dev_1")
        self.assertTrue(self.sec.lock_device("dev_1", 30))
        self.assertTrue(self.sec.is_device_locked("dev_1"))

    def test_token(self):
        token = self.sec.generate_token("dev_1", "api")
        self.assertTrue(self.sec.validate_token(token))
        self.assertTrue(self.sec.revoke_token(token))
        self.assertFalse(self.sec.validate_token(token))

    def test_audit_log(self):
        self.sec.register_device_security("dev_1")
        self.sec.scan_device("dev_1")
        log = self.sec.get_audit_log()
        self.assertGreater(len(log), 0)


class TestMobileConfig(unittest.TestCase):
    def setUp(self):
        self.config = MobileConfig()

    def test_set_get(self):
        self.config.set("theme", "dark")
        self.assertEqual(self.config.get("theme"), "dark")

    def test_delete(self):
        self.config.set("key", "value")
        self.assertTrue(self.config.delete("key"))
        self.assertIsNone(self.config.get("key"))

    def test_override(self):
        self.config.set("theme", "light")
        self.config.set_override("theme", "dev_1", "dark")
        self.assertEqual(self.config.get("theme", device_id="dev_1"), "dark")

    def test_list_entries(self):
        self.config.set("a", 1)
        self.config.set("b", 2)
        self.assertEqual(len(self.config.list_entries()), 2)


class TestMobileEvents(unittest.TestCase):
    def setUp(self):
        self.bus = MobileEventBus()

    def test_publish(self):
        event = self.bus.publish(MobileEventType.DEVICE_CONNECTED, "dev_1")
        self.assertIsNotNone(event)

    def test_subscribe(self):
        received = []
        self.bus.subscribe(MobileEventType.DEVICE_CONNECTED, lambda e: received.append(e))
        self.bus.publish(MobileEventType.DEVICE_CONNECTED, "dev_1")
        self.assertEqual(len(received), 1)

    def test_get_events(self):
        self.bus.publish(MobileEventType.DEVICE_CONNECTED, "dev_1")
        self.bus.publish(MobileEventType.DEVICE_DISCONNECTED, "dev_2")
        events = self.bus.get_events(device_id="dev_1")
        self.assertEqual(len(events), 1)


class TestMobileMetrics(unittest.TestCase):
    def setUp(self):
        self.metrics = MobileMetrics()

    def test_record(self):
        self.metrics.record("latency", 10.0, device_id="dev_1")
        summary = self.metrics.get_summary("latency")
        self.assertEqual(summary.count, 1)
        self.assertEqual(summary.avg_val, 10.0)

    def test_increment(self):
        self.metrics.increment("requests")
        self.metrics.increment("requests")
        self.assertEqual(self.metrics.get_counter("requests"), 2)

    def test_gauge(self):
        self.metrics.set_gauge("battery", 85.0)
        self.assertEqual(self.metrics.get_gauge("battery"), 85.0)

    def test_list_metrics(self):
        self.metrics.record("a", 1.0)
        self.metrics.record("b", 2.0)
        self.assertEqual(len(self.metrics.list_metrics()), 2)


class TestMobileLogger(unittest.TestCase):
    def setUp(self):
        self.logger = MobileLogger()

    def test_log_levels(self):
        self.logger.debug("debug msg")
        self.logger.info("info msg")
        self.logger.warning("warn msg")
        self.logger.error("error msg")
        self.logger.critical("critical msg")
        self.assertEqual(self.logger.count(), 5)

    def test_filter_by_level(self):
        self.logger.info("a")
        self.logger.error("b")
        self.logger.error("c")
        errors = self.logger.get_entries(level=LogLevel.ERROR)
        self.assertEqual(len(errors), 2)

    def test_clear(self):
        self.logger.info("a")
        self.logger.info("b")
        cleared = self.logger.clear()
        self.assertEqual(cleared, 2)
        self.assertEqual(self.logger.count(), 0)


# ═══════════════════════════════════════════════════════════════════════════
# EDGE RUNTIME TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestEdgeRuntime(unittest.TestCase):
    def test_runtime_engine(self):
        e = EdgeRuntimeEngine()
        config = e.configure("dev_1", max_memory_mb=1024)
        self.assertIsNotNone(config)
        self.assertTrue(e.start("dev_1"))
        self.assertEqual(e.get_state("dev_1"), RuntimeState.RUNNING)
        self.assertTrue(e.stop("dev_1"))
        self.assertEqual(e.count(), 1)

    def test_local_model_manager(self):
        m = LocalModelManager()
        model = m.register("nlp", "1.0", 50.0)
        self.assertIsNotNone(model)
        self.assertTrue(m.load(model.model_id))
        self.assertEqual(model.status, LocalModelStatus.LOADED)
        self.assertEqual(m.get_total_size(), 50.0)

    def test_inference_engine(self):
        e = InferenceEngine()
        req = e.submit("model_1", "input data")
        resp = e.process(req)
        self.assertIsNotNone(resp)
        self.assertTrue(resp.success)

    def test_model_manager(self):
        m = EdgeModelManager()
        model = m.add_model("classifier", "2.0")
        self.assertIsNotNone(model)
        self.assertTrue(m.queue_download(model.model_id))
        self.assertTrue(m.complete_download(model.model_id))
        self.assertTrue(m.activate(model.model_id))
        self.assertEqual(model.lifecycle, ModelLifecycle.ACTIVE)

    def test_resource_manager(self):
        r = EdgeResourceManager()
        snap = r.report("dev_1", cpu_percent=45.0, memory_used_mb=200, memory_total_mb=512)
        self.assertIsNotNone(snap)
        self.assertFalse(r.is_over_limit("dev_1"))
        r.set_limits("dev_1", cpu_percent=40.0)
        self.assertTrue(r.is_over_limit("dev_1"))

    def test_accelerator_manager(self):
        a = AcceleratorManager()
        acc = a.register("gpu_0", "gpu", 4, 8192)
        self.assertIsNotNone(acc)
        self.assertTrue(a.acquire("gpu_0"))
        self.assertEqual(acc.status, AcceleratorStatus.IN_USE)
        self.assertTrue(a.release("gpu_0"))
        self.assertEqual(a.count(), 1)


# ═══════════════════════════════════════════════════════════════════════════
# OFFLINE TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestOffline(unittest.TestCase):
    def test_offline_engine(self):
        e = OfflineEngine()
        session = e.enter_offline("dev_1")
        self.assertIsNotNone(session)
        self.assertEqual(session.mode, OfflineMode.ACTIVE)
        e.queue_action({"type": "sync", "data": "test"})
        self.assertEqual(len(e.get_queue()), 1)
        processed = e.process_queue()
        self.assertEqual(len(processed), 1)
        self.assertTrue(e.exit_offline(session.session_id))

    def test_cache_manager(self):
        c = CacheManager(max_size_bytes=10000)
        self.assertTrue(c.put("key1", "data1", 100))
        self.assertEqual(c.get("key1"), "data1")
        self.assertTrue(c.contains("key1"))
        self.assertEqual(c.size(), 1)
        self.assertTrue(c.remove("key1"))
        self.assertFalse(c.contains("key1"))

    def test_local_database(self):
        db = LocalDatabase()
        record = db.insert("users", "u1", {"name": "Alice"})
        self.assertIsNotNone(record)
        found = db.get("users", "u1")
        self.assertIsNotNone(found)
        self.assertTrue(db.update("users", "u1", {"name": "Bob"}))
        self.assertEqual(db.count("users"), 1)
        self.assertTrue(db.delete("users", "u1"))
        self.assertEqual(db.count("users"), 0)

    def test_queue_manager(self):
        q = OfflineQueueManager()
        item = q.enqueue("sync", {"data": "test"}, QueuePriority.HIGH)
        self.assertIsNotNone(item)
        dequeued = q.dequeue()
        self.assertIsNotNone(dequeued)
        self.assertTrue(q.complete(dequeued.item_id))

    def test_sync_queue(self):
        sq = SyncQueue()
        item = sq.add("users", "u1", "upsert", {"name": "Alice"})
        self.assertIsNotNone(item)
        pending = sq.get_pending()
        self.assertEqual(len(pending), 1)
        self.assertTrue(sq.mark_syncing(item.item_id))
        self.assertTrue(sq.mark_synced(item.item_id))
        self.assertEqual(sq.count_pending(), 0)


# ═══════════════════════════════════════════════════════════════════════════
# SYNCHRONIZATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestSynchronization(unittest.TestCase):
    def test_sync_engine(self):
        e = MobileSyncEngine()
        job = e.create_job("sync_users", SyncDirection.BIDIRECTIONAL)
        self.assertIsNotNone(job)
        result = e.execute(job.job_id, push_data=[1, 2, 3])
        self.assertTrue(result["success"])
        self.assertEqual(job.state, SyncState.COMPLETED)

    def test_conflict_resolver(self):
        r = ConflictResolver()
        conflict = r.detect("users", "u1", {"name": "A"}, {"name": "B"})
        self.assertIsNotNone(conflict)
        resolved = r.resolve(conflict.conflict_id, ConflictStrategy.CLIENT_WINS)
        self.assertIsNotNone(resolved)
        self.assertEqual(resolved["name"], "A")

    def test_data_merger(self):
        m = DataMerger()
        result = m.merge({"a": 1, "b": 2}, {"b": 3, "c": 4})
        self.assertIsNotNone(result)
        self.assertEqual(result.merged_data["a"], 1)
        self.assertEqual(result.merged_data["c"], 4)

    def test_cloud_sync(self):
        c = CloudSyncManager()
        config = c.configure("https://api.cloud.com", "key123")
        self.assertIsNotNone(config)
        self.assertEqual(c.get_status(), CloudSyncStatus.CONNECTED)
        result = c.sync_push({"data": "test"})
        self.assertTrue(result["success"])


# ═══════════════════════════════════════════════════════════════════════════
# DEVICES TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestDevices(unittest.TestCase):
    def test_device_engine(self):
        e = DeviceEngine()
        device = e.register("Pixel 8", "android", "14")
        self.assertIsNotNone(device)
        self.assertTrue(e.update_status(device.device_id, DeviceStatus.MAINTENANCE))
        self.assertTrue(e.set_config(device.device_id, "theme", "dark"))
        self.assertTrue(e.add_tag(device.device_id, "mobile"))
        self.assertEqual(e.count(), 1)

    def test_device_registry(self):
        r = DeviceRegistry()
        reg = r.register("dev_1", owner="Alice", department="Engineering")
        self.assertIsNotNone(reg)
        self.assertTrue(r.is_registered("dev_1"))

    def test_device_health(self):
        h = DeviceHealthMonitor()
        report = h.report("dev_1", cpu_usage=45.0, memory_usage=60.0, battery_level=85.0)
        self.assertIsNotNone(report)
        h.set_thresholds("dev_1", cpu=80.0, memory=80.0)
        alerts = h.check_alerts("dev_1")
        self.assertEqual(len(alerts), 0)

    def test_remote_control(self):
        rc = RemoteControlManager()
        result = rc.send_command("dev_1", RemoteCommand.REBOOT)
        self.assertIsNotNone(result)
        self.assertTrue(rc.update_status(result.command_id, CommandStatus.COMPLETED))
        self.assertEqual(result.status, CommandStatus.COMPLETED)

    def test_inventory(self):
        inv = DeviceInventory()
        item = inv.add("INV001", "Pixel 8", category="smartphone", model="Pixel 8 Pro")
        self.assertIsNotNone(item)
        self.assertTrue(inv.assign("INV001", "Alice"))
        self.assertEqual(item.status, "assigned")
        self.assertTrue(inv.unassign("INV001"))
        self.assertEqual(inv.count(), 1)


# ═══════════════════════════════════════════════════════════════════════════
# NOTIFICATIONS TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestNotifications(unittest.TestCase):
    def test_notification_engine(self):
        e = NotificationEngine()
        notif = e.send("Alert", "High CPU usage", NotificationType.PUSH, NotificationPriority.HIGH)
        self.assertIsNotNone(notif)
        self.assertTrue(e.mark_read(notif.notification_id))
        self.assertEqual(e.count_unread(), 0)

    def test_push_manager(self):
        p = PushManager()
        token = p.register_token("dev_1", "android", "token_abc")
        self.assertIsNotNone(token)
        msg = p.send_push("Title", "Body")
        self.assertIsNotNone(msg)

    def test_alert_rules(self):
        a = AlertRuleManager()
        rule = a.create_rule("high_cpu", AlertCondition.THRESHOLD, "cpu_usage", 80.0, ">")
        self.assertIsNotNone(rule)
        self.assertTrue(a.evaluate(rule.rule_id, 90.0))
        self.assertFalse(a.evaluate(rule.rule_id, 50.0))

    def test_templates(self):
        t = TemplateManager()
        tmpl = t.create("welcome", "Welcome User", title_template="Welcome {{name}}!", message_template="Hello {{name}}, welcome to {{app}}")
        self.assertIsNotNone(tmpl)
        rendered = t.render("welcome", {"name": "Alice", "app": "SuperDev"})
        self.assertEqual(rendered["title"], "Welcome Alice!")
        self.assertEqual(rendered["message"], "Hello Alice, welcome to SuperDev")


# ═══════════════════════════════════════════════════════════════════════════
# BIOMETRICS TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestBiometrics(unittest.TestCase):
    def test_biometric_engine(self):
        e = BiometricEngine()
        enrollment = e.enroll("user_1", BiometricType.FINGERPRINT, "template_data", 0.95)
        self.assertIsNotNone(enrollment)
        self.assertTrue(e.is_enrolled("user_1", BiometricType.FINGERPRINT))
        result = e.authenticate("user_1", BiometricType.FINGERPRINT)
        self.assertEqual(result, AuthResult.SUCCESS)
        self.assertTrue(e.revoke(enrollment.enrollment_id))

    def test_fingerprint_manager(self):
        f = FingerprintManager()
        template = f.enroll("user_1", 0, "data", 0.9)
        self.assertIsNotNone(template)
        self.assertTrue(f.verify("user_1", 0))
        self.assertEqual(f.count(), 1)

    def test_face_manager(self):
        f = FaceRecognitionManager()
        template = f.enroll("user_1", [0.1, 0.2, 0.3], 0.95)
        self.assertIsNotNone(template)
        self.assertTrue(f.verify("user_1", [0.1, 0.2, 0.3]))
        self.assertEqual(f.count(), 1)

    def test_voice_manager(self):
        v = VoiceRecognitionManager()
        vp = v.enroll("user_1", [0.5, 0.6, 0.7], 3.0, 0.88)
        self.assertIsNotNone(vp)
        self.assertTrue(v.verify("user_1", [0.5, 0.6, 0.7]))
        self.assertEqual(v.count(), 1)


# ═══════════════════════════════════════════════════════════════════════════
# SUBSYSTEM IMPORT TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestSubsystemImports(unittest.TestCase):
    def test_edge_runtime_imports(self):
        from mobile_edge.edge_runtime import EdgeRuntimeEngine, LocalModelManager, InferenceEngine, EdgeModelManager, EdgeResourceManager, AcceleratorManager
        self.assertTrue(all([EdgeRuntimeEngine, LocalModelManager, InferenceEngine, EdgeModelManager, EdgeResourceManager, AcceleratorManager]))

    def test_offline_imports(self):
        from mobile_edge.offline import OfflineEngine, CacheManager, LocalDatabase, OfflineQueueManager, SyncQueue
        self.assertTrue(all([OfflineEngine, CacheManager, LocalDatabase, OfflineQueueManager, SyncQueue]))

    def test_synchronization_imports(self):
        from mobile_edge.synchronization import MobileSyncEngine, ConflictResolver, DataMerger, CloudSyncManager
        self.assertTrue(all([MobileSyncEngine, ConflictResolver, DataMerger, CloudSyncManager]))

    def test_devices_imports(self):
        from mobile_edge.devices import DeviceEngine, DeviceRegistry, DeviceHealthMonitor, RemoteControlManager, DeviceInventory
        self.assertTrue(all([DeviceEngine, DeviceRegistry, DeviceHealthMonitor, RemoteControlManager, DeviceInventory]))

    def test_notifications_imports(self):
        from mobile_edge.notifications import NotificationEngine, PushManager, AlertRuleManager, TemplateManager
        self.assertTrue(all([NotificationEngine, PushManager, AlertRuleManager, TemplateManager]))

    def test_biometrics_imports(self):
        from mobile_edge.biometrics import BiometricEngine, FingerprintManager, FaceRecognitionManager, VoiceRecognitionManager
        self.assertTrue(all([BiometricEngine, FingerprintManager, FaceRecognitionManager, VoiceRecognitionManager]))


# ═══════════════════════════════════════════════════════════════════════════
# CROSS-SUBSYSTEM INTEGRATION TESTS
# ═══════════════════════════════════════════════════════════════════════════

class TestCrossSubsystemIntegration(unittest.TestCase):
    def test_edge_offline_pipeline(self):
        engine = MobileEngine()
        edge = EdgeEngine()
        offline = OfflineEngine()

        device = engine.register_device("Test Device", PlatformType.ANDROID)
        model = edge.register_model("test_model", "1.0", 50.0)
        edge.load_model(model.model_id)

        session = offline.enter_offline(device.device_id)
        result = edge.infer(model.model_id, "offline input")
        offline.queue_action({"type": "inference", "result": str(result)})

        self.assertIsNotNone(session)
        self.assertIsNotNone(result)
        self.assertEqual(len(offline.get_queue()), 1)

    def test_device_security_biometric_pipeline(self):
        dm = DeviceManager()
        sec = MobileSecurityManager()
        bio = BiometricEngine()

        device = dm.register_device("Secure Phone", DeviceCategory.SMARTPHONE)
        sec.register_device_security(device.device_id)
        sec.create_policy("secure", SecurityLevel.HIGH, require_biometric=True)

        bio.enroll("user_1", BiometricType.FACE, "embedding_data")
        auth_result = bio.authenticate("user_1", BiometricType.FACE)
        self.assertEqual(auth_result, AuthResult.SUCCESS)

        sec.scan_device(device.device_id)
        dev_sec = sec.device_security[device.device_id]
        self.assertEqual(dev_sec.threat_level, ThreatType.NONE)

    def test_notification_sync_pipeline(self):
        notif_engine = NotificationEngine()
        sync_engine = MobileSyncEngine()
        cloud = CloudSyncManager()

        cloud.configure("https://api.cloud.com")
        job = sync_engine.create_job("notify_sync", SyncDirection.PUSH)
        result = sync_engine.execute(job.job_id, push_data={"notifications": [1, 2, 3]})

        notif_engine.send("Sync Complete", f"Pushed {result['pushed']} items", NotificationType.IN_APP)
        self.assertTrue(result["success"])
        self.assertEqual(notif_engine.count(), 1)

    def test_full_lifecycle(self):
        engine = MobileEngine()
        edge = EdgeEngine()
        dm = DeviceManager()
        sec = MobileSecurityManager()
        offline = OfflineEngine()
        sync = MobileSyncEngine()
        notif = NotificationEngine()
        bio = BiometricEngine()

        device = engine.register_device("Enterprise Phone", PlatformType.ANDROID)
        dm.register_device("Enterprise Phone", DeviceCategory.SMARTPHONE)
        sec.register_device_security(device.device_id)

        model = edge.register_model("enterprise_ai", "3.0", 200.0)
        edge.load_model(model.model_id)

        bio.enroll("emp_1", BiometricType.FINGERPRINT)
        auth = bio.authenticate("emp_1", BiometricType.FINGERPRINT)
        self.assertEqual(auth, AuthResult.SUCCESS)

        session = offline.enter_offline(device.device_id)
        result = edge.infer(model.model_id, "enterprise data")
        self.assertIsNotNone(result)

        job = sync.create_job("enterprise_sync")
        sync_result = sync.execute(job.job_id, push_data={"result": "synced"})
        self.assertTrue(sync_result["success"])

        notif.send("Sync Done", "All data synced", NotificationType.PUSH)
        self.assertEqual(notif.count(), 1)


if __name__ == '__main__':
    unittest.main(verbosity=2)
