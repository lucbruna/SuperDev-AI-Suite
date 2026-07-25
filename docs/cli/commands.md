# CLI Commands Reference

## Project Commands

| Command | Description |
|---------|-------------|
| `superdev init <name>` | Create a new project |
| `superdev dev` | Start development server |
| `superdev build` | Build the project |
| `superdev test` | Run tests |
| `superdev lint` | Lint the project |

## Authentication

| Command | Description |
|---------|-------------|
| `superdev login` | Login to SuperDev |
| `superdev logout` | Logout |
| `superdev whoami` | Show current user |

## Agents

| Command | Description |
|---------|-------------|
| `superdev agent list` | List agents |
| `superdev agent start <id>` | Start an agent |
| `superdev agent stop <id>` | Stop an agent |
| `superdev agent logs <id>` | View agent logs |

## Workflows

| Command | Description |
|---------|-------------|
| `superdev workflow list` | List workflows |
| `superdev workflow run <id>` | Run a workflow |
| `superdev workflow create` | Create a workflow |

## Plugins

| Command | Description |
|---------|-------------|
| `superdev plugin list` | List plugins |
| `superdev plugin install <id>` | Install a plugin |
| `superdev plugin uninstall <id>` | Uninstall a plugin |

## AI

| Command | Description |
|---------|-------------|
| `superdev ai chat` | Start AI chat |
| `superdev ai models` | List available models |
| `superdev ai providers` | List providers |

## Runtime

| Command | Description |
|---------|-------------|
| `superdev runtime list` | List runtimes |
| `superdev runtime logs` | View runtime logs |
| `superdev runtime shell` | Open runtime shell |

## Deploy

| Command | Description |
|---------|-------------|
| `superdev deploy` | Deploy to production |
| `superdev deploy --env staging` | Deploy to staging |
| `superdev deploy --rollback` | Rollback deployment |

## System

| Command | Description |
|---------|-------------|
| `superdev doctor` | Check system health |
| `superdev status` | Show platform status |
| `superdev version` | Show version |
| `superdev update` | Update CLI |
