"""Tests for the utils package (Phase I)."""
from __future__ import annotations

import pytest

from modules.autonomous_developer.utils import (
    atomic_write,
    ensure_dir,
    indent,
    read_text,
    safe_join,
    sha256_file,
    slugify,
    truncate,
)


class TestTextHelpers:
    def test_slugify_basic(self):
        assert slugify("Hello World!") == "hello-world"

    def test_slugify_collapses_runs(self):
        assert slugify("  A -- B  ") == "a-b"

    def test_slugify_empty(self):
        assert slugify("") == ""

    def test_truncate_short_text_unchanged(self):
        assert truncate("abcd", 10) == "abcd"

    def test_truncate_long_text(self):
        assert truncate("abcdefghij", 5) == "ab..."

    def test_truncate_custom_suffix(self):
        assert truncate("abcdefghij", 6, suffix="~") == "abcde~"

    def test_truncate_max_shorter_than_suffix(self):
        assert truncate("abcdef", 2) == "ab"

    def test_indent(self):
        assert indent("a\nb", spaces=2) == "  a\n  b"


class TestFileHelpers:
    def test_ensure_dir(self, tmp_path):
        target = ensure_dir(tmp_path / "a" / "b")
        assert target.is_dir()

    def test_atomic_write_and_read_roundtrip(self, tmp_path):
        path = tmp_path / "f.txt"
        atomic_write(path, "hello")
        assert read_text(path) == "hello"

    def test_atomic_write_overwrites(self, tmp_path):
        path = tmp_path / "f.txt"
        atomic_write(path, "one")
        atomic_write(path, "two")
        assert read_text(path) == "two"

    def test_read_text_missing_returns_default(self, tmp_path):
        assert read_text(tmp_path / "nope.txt", default="d") == "d"
        assert read_text(tmp_path / "nope.txt") is None

    def test_sha256_file_known_hash(self, tmp_path):
        path = tmp_path / "f.txt"
        atomic_write(path, "abc")
        assert sha256_file(path) == (
            "ba7816bf8f01cfea414140de5dae2223"
            "b00361a396177a9cb410ff61f20015ad"
        )

    def test_safe_join_within_root(self, tmp_path):
        target = safe_join(tmp_path, "a", "b.py")
        assert target == tmp_path / "a" / "b.py"

    def test_safe_join_escape_raises(self, tmp_path):
        with pytest.raises(ValueError):
            safe_join(tmp_path, "..", "outside.py")
