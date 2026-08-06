# Changelog

All notable changes to the Autonomous Developer module.

## [1.0.0] - 2026-08-05

### Added
- Module scaffold: `__init__.py`, `version.py`, `README.md`, `LICENSE`.
- `config/` package with `SUPERDEV_AD_*` env overrides:
  - `DeveloperConfig` — top-level runtime configuration.
  - `PlannerConfig` — task decomposition and planning behaviour.
  - `GeneratorConfig` — code generation constraints.
  - `LLMConfig` — LLM provider settings.
  - `CodingRules` — code style/quality guardrails.
  - `SecurityRules` — path and secret guardrails.
  - `QualityRules` — test and lint quality gates.
  - `StyleRules` — formatting conventions.
  - `Permissions` — RBAC for AD operations.
