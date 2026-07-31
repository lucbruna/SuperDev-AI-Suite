"""Security regression: ClickHouse credentials are sent via HTTP Basic auth, never in the URL."""

from __future__ import annotations

import asyncio
import base64

from database.database_models import ConnectionConfig
from database.drivers.clickhouse import ClickHouseDriver


def _driver_with_credentials() -> ClickHouseDriver:
    driver = ClickHouseDriver()
    asyncio.run(
        driver.connect(
            ConnectionConfig(
                host="ch.internal", username="analytics", password="s3cr3t!pass", port=8123
            )
        )
    )
    return driver


class TestClickHouseCredentialHandling:
    def test_credentials_use_basic_auth_header(self) -> None:
        driver = _driver_with_credentials()
        expected = base64.b64encode(b"analytics:s3cr3t!pass").decode("ascii")
        assert driver._auth == expected
        # A senha nunca aparece na URL/base.
        assert "s3cr3t" not in driver._base_url
        assert "password" not in driver._base_url
        assert "analytics" not in driver._base_url

    def test_no_username_no_auth_header(self) -> None:
        driver = ClickHouseDriver()
        asyncio.run(driver.connect(ConnectionConfig(host="ch.internal", port=8123)))
        assert driver._auth == ""
