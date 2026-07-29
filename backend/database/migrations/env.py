"""Alembic migration environment.

Usa importlib para carregar models sem disparar backend.__init__
(que tem lazy imports para evitar hangs).
"""

import os
import sys
from logging.config import fileConfig

from sqlalchemy import create_engine
from sqlalchemy import pool

from alembic import context

# Adicionar o diretório raiz ao path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(__file__))))

# Importa o Base usando importlib para evitar passar pelo backend.__init__
import importlib
base_mod = importlib.import_module("backend.database.base")
Base = base_mod.Base

# Importa todos os modelos para registrar no metadata do Base
importlib.import_module("backend.database.models")

config = context.config
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# URL do banco (usa sync driver psycopg2 para migracoes)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://superdev:superdev@localhost:5432/superdev",
)


def run_migrations_offline() -> None:
    """Executa migracoes em modo offline (gera SQL)."""
    url = config.get_main_option("sqlalchemy.url", DATABASE_URL)
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Executa migracoes em modo online (conectado ao banco)."""
    url = os.getenv("DATABASE_URL", DATABASE_URL)
    connectable = create_engine(url, poolclass=pool.NullPool)
    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
        )
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
