"""Tests for the CLI parser and dispatch (Phase I)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.cli import (
    ArgumentParser,
    CLI,
    CLIArgs,
    CLIError,
)


class TestArgumentParser:
    def test_parse_command_only(self):
        args = ArgumentParser().parse(["plan"])
        assert args.command == "plan"
        assert args.options == {}
        assert args.targets == []

    def test_parse_flag_option(self):
        args = ArgumentParser().parse(["run", "--dry-run", "app.py"])
        assert args.command == "run"
        assert args.options == {"dry_run": True}
        assert args.targets == ["app.py"]

    def test_parse_option_with_value(self):
        args = ArgumentParser().parse(["run", "--config", "x.json"])
        assert args.options == {"config": "x.json"}

    def test_parse_mixed(self):
        args = ArgumentParser().parse(
            ["run", "--config", "x.json", "--verbose", "a.py", "b.py"]
        )
        assert args.options == {"config": "x.json", "verbose": True}
        assert args.targets == ["a.py", "b.py"]

    def test_empty_argv_raises(self):
        with pytest.raises(CLIError):
            ArgumentParser().parse([])

    def test_unknown_command_raises(self):
        with pytest.raises(CLIError):
            ArgumentParser().parse(["nope"])

    def test_custom_commands(self):
        parser = ArgumentParser(commands=["build"])
        assert parser.parse(["build"]).command == "build"
        with pytest.raises(CLIError):
            parser.parse(["run"])

    def test_help_text(self):
        text = ArgumentParser().help_text()
        assert "usage: superdev <command>" in text
        assert "  plan" in text
        assert "  help" in text

    def test_cli_args_dataclass(self):
        args = CLIArgs(command="x")
        assert args.options == {}
        assert args.targets == []

    def test_option_without_value_raises(self):
        with pytest.raises(CLIError):
            ArgumentParser().parse(["run", "--config"])


class TestCLI:
    def test_execute_help(self):
        result = CLI().execute(["help"])
        assert result.ok
        assert "usage: superdev" in result.message

    def test_execute_known_command(self):
        result = CLI().execute(["plan", "--dry-run"])
        assert result.ok
        assert result.message == "Executed command: plan"
        assert result.args.options == {"dry_run": True}

    def test_execute_parse_error(self):
        result = CLI().execute(["nope"])
        assert not result.ok
        assert "Unknown command" in result.message

    def test_execute_empty(self):
        result = CLI().execute([])
        assert not result.ok
        assert "No command given" in result.message
