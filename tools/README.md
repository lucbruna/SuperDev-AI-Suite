# SuperDev Tools

Auxiliary tools for development and maintenance.

## Available Tools

| Tool | Description |
|------|-------------|
| `code_generator.py` | Generate boilerplate code |
| `schema_converter.py` | Convert between schema formats |
| `db_migrator.py` | Database migration utilities |

## Usage

```bash
python tools/code_generator.py --template crud --model User
python tools/schema_converter.py --input openapi.yaml --output graphql
python tools/db_migrator.py --from sqlite --to postgres
```
