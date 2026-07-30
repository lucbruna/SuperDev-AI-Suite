from __future__ import annotations

from workflow.integrations.integration_models import Integration, IntegrationStatus
from workflow.integrations.integration_manager import IntegrationManager
from workflow.integrations.integration_http import IntegrationHttp
from workflow.integrations.integration_auth import IntegrationAuth
from workflow.integrations.integration_logger import IntegrationLogger
from workflow.integrations.integration_retry import IntegrationRetry


class TestIntegrations:
    def test_integration_defaults(self) -> None:
        i = Integration(name="test", integration_type="http")
        assert i.name == "test"
        assert i.status == IntegrationStatus.INACTIVE

    def test_integration_manager(self) -> None:
        mgr = IntegrationManager()
        i = Integration(name="test", integration_type="http")
        mgr.add(i)
        assert mgr.get(i.id) == i
        mgr.remove(i.id)
        assert mgr.get(i.id) is None

    def test_integration_http(self) -> None:
        http = IntegrationHttp()
        result = http.get("https://example.com")
        assert result["status"] == "ok"

    def test_integration_auth(self) -> None:
        auth = IntegrationAuth()
        auth.store("i1", {"token": "abc"})
        assert auth.get("i1") == {"token": "abc"}

    def test_integration_logger(self) -> None:
        logger = IntegrationLogger()
        logger.log("i1", "test", "ok")
        history = logger.get_history("i1")
        assert len(history) == 1

    def test_integration_retry(self) -> None:
        calls: list[int] = []
        def fail_twice() -> str:
            calls.append(1)
            if len(calls) < 3:
                raise ConnectionError("fail")
            return "ok"
        retry = IntegrationRetry(max_retries=3, delay=0.01)
        result = retry.execute(fail_twice)
        assert result == "ok"
        assert len(calls) == 3
