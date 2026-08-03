"""Alembic migration environment for the Fleet Maintenance API.

This module configures Alembic to use the application's PostgreSQL
connection settings and SQLAlchemy model metadata when generating and
applying database migrations.
"""

from logging.config import fileConfig

from alembic import context
from sqlalchemy import create_engine, pool

from app import models as _models
from app.database import Base
from app.config import settings


# Alembic provides this Config object when migration commands are run.
config = context.config


# Configure logging from alembic.ini.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)


# Importing app.models registers all SQLAlchemy models with Base.metadata.
# Alembic uses this metadata when comparing Python models to PostgreSQL.
target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Run migrations without establishing a live database connection."""

    context.configure(
        url=settings.database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations using a live PostgreSQL database connection."""

    # Alembic only needs short-lived connections, so persistent connection
    # pooling is unnecessary for migration commands.
    connectable = create_engine(
        settings.database_url,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            compare_type=True,
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()