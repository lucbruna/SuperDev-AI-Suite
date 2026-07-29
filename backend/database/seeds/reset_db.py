#!/usr/bin/env python
"""
Reset database: drop public schema, recreate it, and re-enable extensions.
Usado pelo Makefile (make reset-db / make win-reset-db).

Uso:
    python backend/database/seeds/reset_db.py
"""

from __future__ import annotations

import os

import psycopg2

DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://superdev:superdev@localhost:5432/superdev",
)


def main() -> None:
    conn = psycopg2.connect(DATABASE_URL)
    conn.set_session(autocommit=True)
    cur = conn.cursor()

    # Descobrir qual schema usar (search_path ou current_schema)
    cur.execute("SELECT current_schema()")
    schema = cur.fetchone()[0]
    print(f"[INFO] Schema atual: {schema}")

    # Drop e recria o schema atual
    cur.execute(f'DROP SCHEMA IF EXISTS "{schema}" CASCADE')
    cur.execute(f'CREATE SCHEMA "{schema}"')
    cur.execute(f'GRANT ALL ON SCHEMA "{schema}" TO CURRENT_USER')

    # Re-habilita extensoes necessarias (extension vectors sao globais)
    cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
    cur.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')

    cur.close()
    conn.close()
    print(f"[OK] Schema resetado: {schema}, vector + uuid-ossp habilitados")


if __name__ == "__main__":
    main()
