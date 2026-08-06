# Changelog

All notable changes to this module are documented in this file.

## [1.0.0] - 2026-08-05

### Added
- Módulo Self-Healing Engine inicial:
  - `config/`: HealingConfig, RepairRulesConfig, RecoveryConfig, AutomationConfig,
    SecurityPolicy, RiskPolicy, Permissions e constantes compartilhadas.
  - Fluxo de healing: detecção → diagnóstico → planejamento → validação →
    aprovação → execução → rollback → documentação.
  - Políticas de segurança e risco com aprovação por nível de risco.
