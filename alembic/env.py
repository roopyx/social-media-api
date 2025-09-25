from logging.config import fileConfig
from sqlalchemy import create_engine
from sqlalchemy import pool
from alembic import context

from api.config import config
from api.database import metadata  # metadata con posts y comments

# Configuración de logging
if context.config.config_file_name is not None:
    fileConfig(context.config.config_file_name)

target_metadata = metadata

# URL de la DB
DATABASE_URL = config.DATABASE_URL
print("DATABASE_URL:", DATABASE_URL)

# 🔹 Engine Síncrono para Alembic
# Si tu URL es async (postgresql+asyncpg), reemplaza "+asyncpg" por ""
sync_url = DATABASE_URL.replace("+asyncpg", "")
connectable = create_engine(sync_url, poolclass=pool.NullPool)


def run_migrations_offline():
    context.configure(
        url=sync_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online():
    with connectable.connect() as connection:
        context.configure(connection=connection, target_metadata=target_metadata)
        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
