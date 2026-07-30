"""Tests for k6 load test scripts."""
from __future__ import annotations

from pathlib import Path

import pytest


LOADTESTS_DIR = Path(__file__).resolve().parent.parent.parent / "loadtests"


class TestLoadTestFiles:
    def test_loadtests_directory_exists(self):
        assert LOADTESTS_DIR.exists(), "loadtests/ directory must exist"

    def test_config_file_exists(self):
        assert (LOADTESTS_DIR / "config.js").exists()

    def test_smoke_file_exists(self):
        assert (LOADTESTS_DIR / "smoke.js").exists()

    def test_load_file_exists(self):
        assert (LOADTESTS_DIR / "load.js").exists()

    def test_stress_file_exists(self):
        assert (LOADTESTS_DIR / "stress.js").exists()

    def test_spike_file_exists(self):
        assert (LOADTESTS_DIR / "spike.js").exists()

    def test_endurance_file_exists(self):
        assert (LOADTESTS_DIR / "endurance.js").exists()


class TestLoadTestContent:
    def _read(self, name: str) -> str:
        return (LOADTESTS_DIR / name).read_text()

    def test_config_has_base_url(self):
        content = self._read("config.js")
        assert "BASE_URL" in content
        assert "API_TOKEN" in content

    def test_smoke_has_vus(self):
        content = self._read("smoke.js")
        assert "vus" in content
        assert "duration" in content

    def test_load_has_stages(self):
        content = self._read("load.js")
        assert "stages" in content

    def test_stress_has_stages(self):
        content = self._read("stress.js")
        assert "stages" in content

    def test_spike_has_stages(self):
        content = self._read("spike.js")
        assert "stages" in content

    def test_endurance_has_stages(self):
        content = self._read("endurance.js")
        assert "stages" in content

    def test_smoke_imports_config(self):
        content = self._read("smoke.js")
        assert "import" in content
        assert "config.js" in content

    def test_all_scripts_have_handle_summary(self):
        for name in ["smoke.js", "load.js", "stress.js", "spike.js", "endurance.js"]:
            content = self._read(name)
            assert "handleSummary" in content, f"{name} must have handleSummary"

    def test_all_scripts_use_check(self):
        for name in ["smoke.js", "load.js", "stress.js", "spike.js", "endurance.js"]:
            content = self._read(name)
            assert "check(" in content, f"{name} must use k6 check()"
