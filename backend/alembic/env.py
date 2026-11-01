from logging.config import fileConfig
import sys
import os

# Add parent directory to path for app imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

# Import app models and config
from app.db.base import Base
from app.core.config import settings

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
target_metadata = Base.metadata

# Override sqlalchemy.url with app settings (use sync driver for alembic)
sync_url = settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql+psycopg2://")

# For SQLite, use sync driver
if "sqlite+aiosqlite" in sync_url:
    sync_url = sync_url.replace("sqlite+aiosqlite://", "sqlite://")

# For autogenerate without a live DB, fall back to SQLite in-memory
import os
if os.environ.get("ALEMBIC_OFFLINE") == "1":
    config.set_main_option("sqlalchemy.url", "sqlite://")
else:
    config.set_main_option("sqlalchemy.url", sync_url)


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = engine_from_config(
        config.get_section(config.config_ini_section, {}),
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    try:
        with connectable.connect() as connection:
            context.configure(
                connection=connection, target_metadata=target_metadata
            )

            with context.begin_transaction():
                context.run_migrations()
    except Exception as e:
        # If DB is unavailable (e.g., CI without DB), use SQLite for autogenerate
        if "Connection refused" in str(e) or "could not connect" in str(e).lower():
            print("Database unavailable, using SQLite for autogenerate...")
            from sqlalchemy import create_engine
            sqlite_engine = create_engine("sqlite://")
            with sqlite_engine.connect() as connection:
                context.configure(
                    connection=connection, target_metadata=target_metadata
                )
                with context.begin_transaction():
                    context.run_migrations()
        else:
            raise


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()