"""Database migration utility tool."""

import argparse
from pathlib import Path


def generate_migration(name: str, version: int) -> str:
    return f'''"""Migration {version:04d}: {name}"""

revision = "{version:04d}"
down_revision = None


def upgrade():
    """Apply migration."""
    pass


def downgrade():
    """Rollback migration."""
    pass
'''


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Database migration utilities")
    parser.add_argument("action", choices=["create", "list"])
    parser.add_argument("--name", help="Migration name")
    parser.add_argument("--version", type=int, default=1)
    args = parser.parse_args()

    if args.action == "create":
        if not args.name:
            print("Migration name is required")
            exit(1)
        content = generate_migration(args.name, args.version)
        filepath = Path(f"migrations/{args.version:04d}_{args.name}.py")
        filepath.parent.mkdir(parents=True, exist_ok=True)
        filepath.write_text(content)
        print(f"Created: {filepath}")
    elif args.action == "list":
        for f in sorted(Path("migrations").glob("*.py")):
            print(f.name)
