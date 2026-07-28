from __future__ import annotations

import asyncio
import os
import sys
from typing import Any

import pytest


@pytest.fixture
def client():
    from cli.client import APIClient
    c = APIClient()
    yield c
    asyncio.run(c.close())


class TestInit:
    def test_init_creates_files(self, tmp_path):
        from cli.commands.init import init
        os.chdir(tmp_path)
        try:
            init()
        except SystemExit:
            pass
        assert any(tmp_path.iterdir()), "init should create project files"


class TestDoctor:
    def test_doctor_runs(self, capsys):
        from cli.commands.doctor import doctor
        try:
            doctor()
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "SuperDev" in captured.out or captured.err


class TestDev:
    def test_dev_default_port(self, capsys):
        from cli.commands.dev import dev
        try:
            dev(watch=False, port=3000)
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "3000" in captured.out


class TestTest:
    def test_test_default_path(self, capsys):
        from cli.commands.test import test
        try:
            test(path="tests/", verbose=False, coverage=False)
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "tests/" in captured.out or "passed" in captured.out


class TestLint:
    def test_lint_default_path(self, capsys):
        from cli.commands.lint import lint
        try:
            lint(path=".", fix=False, strict=False)
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "Linting" in captured.out


class TestUpdate:
    def test_update_check(self, capsys):
        from cli.commands.update import update
        try:
            update(check=True, force=False)
        except SystemExit:
            pass
        captured = capsys.readouterr()
        assert "up to date" in captured.out


class TestMainCommands:
    def test_all_commands_registered(self):
        from cli.main import app
        cmds = {c.name for c in app.registered_commands}
        expected = {"init", "doctor", "run", "build", "deploy", "dev", "test", "lint", "update", "eval", "agent", "workflow", "completion", "login", "logout", "status", "version"}
        assert expected.issubset(cmds), f"Missing commands: {expected - cmds}"