# CLI Documentation

## Commands

See the main [CLI commands reference](../../docs/cli/commands.md) for the full list.

## Configuration

The CLI reads configuration from:

1. `~/.superdev/config.yaml` (global)
2. `./.superdev.yaml` (project)
3. Environment variables (`SUPERDEV_*`)

## Shell Completion

```bash
superdev completion bash >> ~/.bashrc
superdev completion zsh >> ~/.zshrc
superdev completion fish >> ~/.config/fish/completions/superdev.fish
superdev completion powershell >> $PROFILE
```
