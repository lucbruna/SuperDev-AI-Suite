# Governance — Quality, Versioning & Metadata Standards

Phase 4 of the meta/quality roadmap. This document codifies the process layer that
enforces the file-quality, versioning, and metadata standards implemented in
Phases 1–3. It is process, not code — the enforcement mechanisms already exist
(`scripts/check_file_quality.py`, `scripts/sync_version.py`, pre-commit hooks,
GitHub Actions quality gates).

---

## 1. Versioning

- **Single source of truth:** the first line of `./VERSION` is the project version,
  formatted as strict semver `X.Y.Z` (e.g. `6.0.0`).
- `VERSION` may carry build-metadata lines after the first line (Commit, Branch,
  Build Date). These are informational only and are ignored by tooling.
- **Enforcement:** `scripts/sync_version.py --check` fails if any package/module
  version metadata diverges from `./VERSION`. Run it in CI and as a pre-commit gate.

## 2. File quality gates

`scripts/check_file_quality.py` validates, in one pass:

| Target | Check |
| ------ | ----- |
| `coverage.json` | valid JSON, no duplicate keys, required schema fields present |
| `VERSION` | first line is valid semver |
| `__init__.py` | every package `__init__.py` parses as valid Python |

- **Enforcement:** local pre-commit hook `file-quality`
  (`pass_filenames: false`, `always_run: true`) and the `quality-gates.yml` workflow.

## 3. Configuration consolidation

- **pytest:** options live in `pyproject.toml` under `[tool.pytest.ini_options]`
  (testpaths, asyncio loop scope, addopts). Do not reintroduce `pytest.ini`.
- **mypy:** options live in `pyproject.toml` under `[tool.mypy]`. Do not reintroduce
  `mypy.ini`.
- **Rule:** one config location per tool. New tool config goes into `pyproject.toml`
  unless the tool requires its own file.

## 4. Skill metadata

- Every skill directory must contain a `.skill-meta.json` following the schema in
  `docs/templates/.skill-meta.template.json`:
  `name`, `description`, `version`, `author`, `created_at`, `updated_at`,
  `dependencies`, `skills`, `entrypoint`.
- `entrypoint` is the skill's primary file (e.g. `SKILL.md`).
- **Note:** `.claude/skills/*` are junctions to `.agents/skills/*` — the same
  physical file is tracked under both paths. Update either; keep them in sync.

## 5. Documentation templates

- `docs/templates/` holds canonical templates:
  - `mantis-summary.template.md` — directory security summaries
  - `__init__.py.template.md` — package docstring convention
  - `.skill-meta.template.json` — skill metadata schema
- New docs/metadata should be generated from these templates, not ad hoc.

## 6. CI/CD

- `ci.yml` — main CI/CD (lint, format, tests, build) on `main`/`develop`.
- `quality-gates.yml` — metadata/quality gate workflow.
- Workflow files must be UTF-8 (no BOM). UTF-16LE files break GitHub Actions.

## 7. Commit discipline

- Commit only the files belonging to the change; do not sweep unrelated WIP into a
  feature commit.
- Prefer conventional-commit messages (`feat`, `fix`, `chore`, `docs`, `refactor`).

---

*Last updated: 2026-08-03*