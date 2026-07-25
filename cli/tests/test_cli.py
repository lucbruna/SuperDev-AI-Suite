"""Tests for the SuperDev CLI."""

import pytest
from unittest.mock import patch, MagicMock


def test_version_output():
    from cli.main import __version__
    assert __version__ is not None


def test_help_output(capsys):
    import sys
    from cli.main import main

    with patch("sys.argv", ["superdev", "--help"]):
        with pytest.raises(SystemExit) as exc_info:
            main()
        assert exc_info.value.code == 0
