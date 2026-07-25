# SuperDev CLI

A CLI do SuperDev fornece acesso via linha de comando a todas as funcionalidades da plataforma.

## Instalação

```bash
pip install superdev-cli
# ou
npm install -g superdev-cli
```

## Início Rápido

```bash
superdev init meu-projeto --template fastapi
superdev login
superdev doctor
superdev dev
```

## Comandos

Consulte [commands.md](commands.md) para a referência completa.

## Configuração

A CLI lê configurações de:
1. `~/.superdev/config.yaml` (global)
2. `./.superdev.yaml` (projeto)
3. Variáveis de ambiente (`SUPERDEV_*`)

## Autocompletar Shell

```bash
superdev completion bash >> ~/.bashrc
superdev completion zsh >> ~/.zshrc
superdev completion powershell >> $PROFILE
```
