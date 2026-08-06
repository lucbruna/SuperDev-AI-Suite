"""Tests for the docs manifest (Phase J)."""
from __future__ import annotations

from modules.autonomous_developer.docs import DocsManifest, ModuleDocs


def build_fake_root(tmp_path):
    """Create a module root with two packages and one non-package dir."""
    (tmp_path / "pkg_a").mkdir()
    (tmp_path / "pkg_a" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg_a" / "one.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg_a" / "two.py").write_text("", encoding="utf-8")
    (tmp_path / "pkg_b").mkdir()
    (tmp_path / "pkg_b" / "__init__.py").write_text("", encoding="utf-8")
    (tmp_path / "not_a_package").mkdir()
    (tmp_path / "not_a_package" / "file.py").write_text("", encoding="utf-8")
    (tmp_path / "loose.py").write_text("", encoding="utf-8")
    return tmp_path


class TestDocsManifest:
    def test_scan_counts_and_excludes_non_packages(self, tmp_path):
        root = build_fake_root(tmp_path)
        entries = DocsManifest().scan(root)
        assert entries == [
            ModuleDocs(package="pkg_a", module_count=2),
            ModuleDocs(package="pkg_b", module_count=0),
        ]

    def test_scan_missing_root(self, tmp_path):
        assert DocsManifest().scan(tmp_path / "nope") == []

    def test_render_index(self, tmp_path):
        root = build_fake_root(tmp_path)
        text = DocsManifest().render_index(root)
        assert text.startswith("# Autonomous Developer Module\n\n")
        assert "- `pkg_a`: 2 module(s)" in text
        assert "- `pkg_b`: 0 module(s)" in text
        assert "not_a_package" not in text

    def test_render_index_empty(self, tmp_path):
        assert DocsManifest().render_index(tmp_path) == (
            "# Autonomous Developer Module\n\n_no packages_\n"
        )

    def test_scan_is_sorted(self, tmp_path):
        root = build_fake_root(tmp_path)
        names = [entry.package for entry in DocsManifest().scan(root)]
        assert names == sorted(names)
