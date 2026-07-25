# SuperDev Project Templates

Templates available via `superdev init --template <name>`:

| Template | Description |
|----------|-------------|
| `fastapi` | Python FastAPI backend with SQLAlchemy |
| `react` | React + Vite + TypeScript + Tailwind |
| `next` | Next.js full-stack application |
| `node` | Express.js + TypeScript backend |
| `python` | Python project with pyproject.toml |
| `flutter` | Flutter mobile application |
| `electron` | Electron desktop application |

## Usage

```bash
superdev init my-project --template fastapi
superdev init my-app --template react
```

## Creating Custom Templates

1. Create a directory under `templates/`
2. Add your project files
3. Include a `README.md` with setup instructions
4. The template will be automatically discovered
