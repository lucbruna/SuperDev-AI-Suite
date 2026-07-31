#!/usr/bin/env python
"""
Runner para popular o banco PostgreSQL com dados iniciais.

Uso:
    python -m backend.database.seeds.run_seeds

Requer:
    - PostgreSQL rodando (via Docker ou diretamente)
    - Variável DATABASE_URL ou default config
"""

from __future__ import annotations

# ── Configuração da conexão ──────────────────────────────────────
# Tenta ler DATABASE_URL do ambiente, fallback para default local
import os
import time

from sqlalchemy import create_engine, text

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://superdev:superdev@localhost:5432/superdev")


def main() -> None:
    t0 = time.time()

    print(f"[CONNECT] Conectando a: {DATABASE_URL}")
    engine = create_engine(DATABASE_URL, pool_pre_ping=True)

    # Verificar conexão
    with engine.connect() as conn:
        result = conn.execute(text("SELECT version()"))
        pg_version = result.scalar()
        print(f"[OK] PostgreSQL conectado: {pg_version[:50]}...")

        # Verificar extensões
        result = conn.execute(text("SELECT extname FROM pg_extension"))
        extensions = [r[0] for r in result]
        print(f"[EXT] Extensoes: {extensions}")

    # ── Executar seeds ──────────────────────────────────────────
    from sqlalchemy.orm import Session

    with Session(engine) as session:
        print("\n=== Seed de Roles e Permissoes ===")
        from backend.database.seeds.roles import seed_roles_and_permissions

        seed_roles_and_permissions(session)

        print("\n=== Seed de Dados (usuarios, orgs, projetos, etc.) ===")
        from backend.database.seeds.seed_data import seed_database

        seed_database(session)

    elapsed = time.time() - t0
    print(f"\n[DONE] Todos os seeds concluidos em {elapsed:.1f}s")


if __name__ == "__main__":
    main()
