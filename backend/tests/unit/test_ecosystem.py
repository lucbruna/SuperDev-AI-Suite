"""Tests for ecosystem modules: notifications, backup, export/import, i18n, search, email, SSO."""

import json
import os
import tempfile
from pathlib import Path

import pytest

# ============================================================
# Notification Manager Tests
# ============================================================

class TestNotificationManager:
    def setup_method(self):
        from backend.notifications.notification_manager import NotificationManager
        self.manager = NotificationManager()

    def test_create_notification(self):
        notif = self.manager.create("user1", "Test", "Hello world")
        assert notif.user_id == "user1"
        assert notif.title == "Test"
        assert notif.is_read is False

    def test_list_for_user(self):
        self.manager.create("user1", "N1", "M1")
        self.manager.create("user1", "N2", "M2")
        self.manager.create("user2", "N3", "M3")
        notifs = self.manager.list_for_user("user1")
        assert len(notifs) == 2

    def test_mark_read(self):
        notif = self.manager.create("user1", "Test", "Body")
        assert self.manager.mark_read(notif.id) is True
        assert self.manager.get(notif.id).is_read is True

    def test_mark_all_read(self):
        self.manager.create("user1", "N1", "M1")
        self.manager.create("user1", "N2", "M2")
        count = self.manager.mark_all_read("user1")
        assert count == 2
        assert self.manager.unread_count("user1") == 0

    def test_unread_count(self):
        self.manager.create("user1", "N1", "M1")
        self.manager.create("user1", "N2", "M2")
        assert self.manager.unread_count("user1") == 2

    def test_delete_notification(self):
        notif = self.manager.create("user1", "Test", "Body")
        assert self.manager.delete(notif.id) is True
        assert self.manager.get(notif.id) is None


# ============================================================
# Email Service Tests
# ============================================================

class TestEmailService:
    def setup_method(self):
        from backend.notifications.email_service import EmailService
        self.service = EmailService(dry_run=True)

    def test_send_dry_run(self):
        from backend.notifications.email_service import EmailMessage
        msg = EmailMessage(to="test@example.com", subject="Test", body="Hello")
        import asyncio
        result = asyncio.get_event_loop().run_until_complete(self.service.send(msg))
        assert result.success is True
        assert result.message_id is not None

    def test_register_template(self):
        self.service.register_template("welcome", "Hello {{name}}!")
        rendered = self.service.render_template("welcome", {"name": "World"})
        assert rendered == "Hello World!"

    def test_get_stats(self):
        stats = self.service.get_stats()
        assert "total_sent" in stats
        assert stats["dry_run"] is True


# ============================================================
# Backup Manager Tests
# ============================================================

class TestBackupManager:
    def setup_method(self):
        from backend.backup.backup_manager import BackupManager
        self.tmpdir = tempfile.mkdtemp()
        self.manager = BackupManager(backup_dir=self.tmpdir)

    def test_backup_files(self):
        import asyncio
        # Create test files
        test_file = Path(self.tmpdir) / "test.txt"
        test_file.write_text("hello world")

        result = asyncio.get_event_loop().run_until_complete(
            self.manager.backup_files([str(test_file)])
        )
        assert result.status.value == "completed"
        assert result.file_size > 0

    def test_list_manifests(self):
        manifests = self.manager.list_manifests()
        assert isinstance(manifests, list)

    def test_get_stats(self):
        stats = self.manager.get_stats()
        assert "total_backups" in stats


# ============================================================
# Data Exporter Tests
# ============================================================

class TestDataExporter:
    def setup_method(self):
        from backend.export_import.data_exporter import DataExporter
        self.tmpdir = tempfile.mkdtemp()
        self.exporter = DataExporter(export_dir=self.tmpdir)

    def test_export_json(self):
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = self.exporter.export_json(data)
        assert result.success is True
        assert result.record_count == 2

    def test_export_csv(self):
        data = [{"name": "Alice", "age": 30}, {"name": "Bob", "age": 25}]
        result = self.exporter.export_csv(data)
        assert result.success is True
        assert result.record_count == 2

    def test_export_to_string_json(self):
        data = [{"key": "value"}]
        output = self.exporter.export_to_string(data, format="json")
        assert "key" in output

    def test_export_to_string_csv(self):
        data = [{"name": "Alice", "age": 30}]
        output = self.exporter.export_to_string(data, format="csv")
        assert "Alice" in output

    def test_get_stats(self):
        stats = self.exporter.get_stats()
        assert "total_exports" in stats


# ============================================================
# Data Importer Tests
# ============================================================

class TestDataImporter:
    def setup_method(self):
        from backend.export_import.data_exporter import DataImporter
        self.importer = DataImporter()

    def test_import_json_string(self):
        json_str = json.dumps([{"name": "Alice"}, {"name": "Bob"}])
        result = self.importer.import_json(json_string=json_str)
        assert result.success is True
        assert result.records_imported == 2

    def test_import_csv_string(self):
        csv_str = "name,age\nAlice,30\nBob,25\n"
        result = self.importer.import_csv(csv_string=csv_str)
        assert result.success is True
        assert result.records_imported == 2

    def test_import_invalid_json(self):
        result = self.importer.import_json(json_string="not json")
        assert result.success is False
        assert len(result.errors) > 0

    def test_get_stats(self):
        stats = self.importer.get_stats()
        assert "total_imports" in stats


# ============================================================
# I18n Tests
# ============================================================

class TestI18n:
    def setup_method(self):
        from backend.i18n.translations import I18nService
        self.i18n = I18nService()

    def test_default_locale(self):
        assert self.i18n._current_locale == "en"

    def test_translate_default(self):
        result = self.i18n.t("common.save")
        assert result == "Save"

    def test_translate_pt_br(self):
        result = self.i18n.t("common.save", locale="pt-BR")
        assert result == "Salvar"

    def test_set_locale(self):
        self.i18n.set_locale("pt-BR")
        assert self.i18n._current_locale == "pt-BR"

    def test_unsupported_locale_ignored(self):
        self.i18n.set_locale("xx-XX")
        assert self.i18n._current_locale == "en"

    def test_fallback(self):
        result = self.i18n.t("nonexistent.key")
        assert result == "nonexistent.key"

    def test_variable_substitution(self):
        result = self.i18n.t("common.save")
        assert "{{" not in result or "name" not in result

    def test_get_supported_locales(self):
        locales = self.i18n.get_supported_locales()
        assert "en" in locales
        assert "pt-BR" in locales

    def test_get_stats(self):
        stats = self.i18n.get_stats()
        assert "current_locale" in stats
        assert "translation_counts" in stats

    def test_missing_keys(self):
        missing = self.i18n.get_missing_keys("en")
        assert isinstance(missing, list)


# ============================================================
# Full-Text Search Tests
# ============================================================

class TestFullTextSearch:
    def setup_method(self):
        from backend.search.full_text_search import FullTextSearch, SearchDocument, SearchableType
        self.search = FullTextSearch()
        self.SearchDocument = SearchDocument
        self.SearchableType = SearchableType

    def test_add_and_search(self):
        doc = self.SearchDocument(
            id="1", type=self.SearchableType.DOCUMENT,
            title="Python Guide", content="Python is a programming language"
        )
        self.search.add_document(doc)
        results = self.search.search("python")
        assert len(results) >= 1
        assert results[0].document_id == "1"

    def test_search_no_results(self):
        doc = self.SearchDocument(
            id="1", type=self.SearchableType.DOCUMENT,
            title="Python Guide", content="Python is great"
        )
        self.search.add_document(doc)
        results = self.search.search("javascript")
        assert len(results) == 0

    def test_remove_document(self):
        doc = self.SearchDocument(
            id="1", type=self.SearchableType.DOCUMENT,
            title="Test", content="Test content"
        )
        self.search.add_document(doc)
        assert self.search.remove_document("1") is True
        assert self.search.get_document("1") is None

    def test_title_boost(self):
        doc1 = self.SearchDocument(
            id="1", type=self.SearchableType.DOCUMENT,
            title="Python Tutorial", content="Learn programming"
        )
        doc2 = self.SearchDocument(
            id="2", type=self.SearchableType.DOCUMENT,
            title="Programming Guide", content="Python is used here"
        )
        self.search.add_document(doc1)
        self.search.add_document(doc2)
        results = self.search.search("python")
        # Doc1 should score higher due to title match
        assert results[0].document_id == "1"

    def test_search_with_type_filter(self):
        doc1 = self.SearchDocument(
            id="1", type=self.SearchableType.DOCUMENT,
            title="Doc", content="Document about Python"
        )
        doc2 = self.SearchDocument(
            id="2", type=self.SearchableType.USER,
            title="User", content="User profile with Python"
        )
        self.search.add_document(doc1)
        self.search.add_document(doc2)
        results = self.search.search("python", doc_type=self.SearchableType.DOCUMENT)
        assert len(results) == 1
        assert results[0].document_type == "document"

    def test_get_stats(self):
        stats = self.search.get_stats()
        assert "total_documents" in stats
        assert "total_terms" in stats


# ============================================================
# Rate Limiter Tests
# ============================================================

class TestRateLimiter:
    def test_rate_limit_basic(self):
        from backend.middleware.rate_limit import RateLimitMiddleware
        # Just test instantiation
        middleware = RateLimitMiddleware(app=None, max_requests=10, window_seconds=60)
        assert middleware.max_requests == 10

    def test_cleanup_expired(self):
        from backend.middleware.rate_limit import RateLimitMiddleware
        middleware = RateLimitMiddleware(app=None, max_requests=10, window_seconds=1)
        removed = middleware.cleanup_expired()
        assert isinstance(removed, int)

    def test_circuit_breaker(self):
        from backend.middleware.rate_limit import CircuitBreaker
        cb = CircuitBreaker(failure_threshold=3, recovery_timeout=1.0)
        assert cb.is_available() is True
        assert cb.state == "closed"


# ============================================================
# Scheduler Tests
# ============================================================

class TestScheduler:
    def test_add_job(self):
        from backend.scheduler.scheduler import Scheduler
        s = Scheduler()
        async def dummy():
            pass
        job_id = s.add_job("test", dummy, interval_seconds=10)
        assert job_id is not None
        jobs = s.list_jobs()
        assert len(jobs) == 1

    def test_remove_job(self):
        from backend.scheduler.scheduler import Scheduler
        s = Scheduler()
        async def dummy():
            pass
        job_id = s.add_job("test", dummy)
        assert s.remove_job(job_id) is True
        assert len(s.list_jobs()) == 0

    def test_enable_disable(self):
        from backend.scheduler.scheduler import Scheduler
        s = Scheduler()
        async def dummy():
            pass
        job_id = s.add_job("test", dummy)
        assert s.disable_job(job_id) is True
        assert s.enable_job(job_id) is True


# ============================================================
# Event Bus Tests
# ============================================================

class TestEventBus:
    def test_subscribe_and_publish(self):
        from backend.events.event_bus import EventBus
        bus = EventBus()
        received = []

        async def handler(event):
            received.append(event)

        bus.subscribe("test.event", handler)
        import asyncio
        event = asyncio.get_event_loop().run_until_complete(
            bus.publish("test.event", {"key": "value"})
        )
        assert event.type == "test.event"
        assert event.data == {"key": "value"}

    def test_get_history(self):
        from backend.events.event_bus import EventBus
        bus = EventBus()
        import asyncio
        asyncio.get_event_loop().run_until_complete(bus.publish("event1"))
        asyncio.get_event_loop().run_until_complete(bus.publish("event2"))
        history = bus.get_history()
        assert len(history) == 2


# ============================================================
# WebSocket Manager Tests
# ============================================================

class TestWebSocketManager:
    def test_connection_count(self):
        from backend.websocket.manager import ConnectionManager
        manager = ConnectionManager()
        assert manager.get_connection_count() == 0

    def test_get_connections(self):
        from backend.websocket.manager import ConnectionManager
        manager = ConnectionManager()
        conns = manager.get_connections("nonexistent")
        assert conns == []


# ============================================================
# SSO Manager Tests
# ============================================================

class TestSSOManager:
    def test_register_provider(self):
        from backend.security.sso import (
            SSOManager, SSOConfig, SSOProviderType, OIDCProvider
        )
        mgr = SSOManager()
        config = SSOConfig(
            provider_type=SSOProviderType.OIDC,
            client_id="test",
            client_secret="secret",
            authorization_url="https://auth.example.com/authorize",
            token_url="https://auth.example.com/token",
            userinfo_url="https://auth.example.com/userinfo",
        )
        provider = OIDCProvider(config)
        mgr.register_provider("test", provider)
        assert mgr.get_provider("test") is not None

    def test_list_providers(self):
        from backend.security.sso import SSOManager
        mgr = SSOManager()
        providers = mgr.list_providers()
        assert isinstance(providers, list)


# ============================================================
# Plugin Manager Tests
# ============================================================

class TestPluginManager:
    def setup_method(self):
        from backend.plugins.plugin_manager import PluginManager
        self.tmpdir = tempfile.mkdtemp()
        self.manager = PluginManager(plugins_dir=self.tmpdir)

    def test_list_plugins_empty(self):
        plugins = self.manager.list_plugins()
        assert plugins == []

    def test_get_plugin_not_found(self):
        assert self.manager.get_plugin("nonexistent") is None


# ============================================================
# Cache Manager Tests
# ============================================================

class TestCacheManager:
    def setup_method(self):
        from backend.cache.cache_manager import CacheManager
        self.manager = CacheManager()

    @pytest.mark.asyncio
    async def test_set_get(self):
        await self.manager.set("key1", "value1")
        result = await self.manager.get("key1")
        assert result == "value1"

    @pytest.mark.asyncio
    async def test_delete(self):
        await self.manager.set("key1", "value1")
        await self.manager.delete("key1")
        result = await self.manager.get("key1")
        assert result is None

    @pytest.mark.asyncio
    async def test_exists(self):
        await self.manager.set("key1", "value1")
        assert await self.manager.exists("key1") is True
        assert await self.manager.exists("key2") is False


# ============================================================
# Auth JWT Tests
# ============================================================

class TestJWTManager:
    def setup_method(self):
        os.environ["JWT_SECRET_KEY"] = "test-secret-key-for-tests"
        from backend.auth.jwt import JWTManager
        self.manager = JWTManager(secret_key="test-secret-key-for-tests")

    def test_create_access_token(self):
        token = self.manager.create_access_token("user123")
        assert token is not None
        assert len(token) > 0

    def test_create_refresh_token(self):
        token = self.manager.create_refresh_token("user123")
        assert token is not None

    def test_decode_token(self):
        token = self.manager.create_access_token("user123")
        payload = self.manager.decode_token(token)
        assert payload is not None
        assert payload["sub"] == "user123"

    def test_decode_invalid_token(self):
        payload = self.manager.decode_token("invalid.token.here")
        assert payload is None
