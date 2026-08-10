"""
Alembic environment configuration.

Reads the real database connection string from the DATABASE_URL environment
variable (see backend/.env.example) rather than from alembic.ini, so
credentials never end up in version control.
"""
import os
import sys
from logging.config import fileConfig

from alembic import context
from dotenv import load_dotenv
from sqlalchemy import create_engine, engine_from_config, pool

# Make "app" importable when alembic is run from the backend/ directory.
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

# Load backend/.env so DATABASE_URL is available the same way it is for
# the running app — without this, Alembic only sees real OS environment
# variables, not values from the .env file.
load_dotenv(os.path.join(os.path.dirname(__file__), "..", ".env"))

from app.models import Base  # noqa: E402  (import after sys.path fix)

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# NOTE: we deliberately do NOT pass the URL through
# config.set_main_option()/ConfigParser. ConfigParser treats "%" as the
# start of interpolation syntax, and URL-encoded passwords (e.g. "%40"
# for "@") crash it with "invalid interpolation syntax". We keep the raw
# URL in a plain Python variable instead and build the engine directly.
database_url = os.environ.get("DATABASE_URL")

target_metadata = Base.metadata


def run_migrations_offline() -> None:
    """Generate SQL scripts without a live DB connection (alembic upgrade --sql)."""
    url = database_url or config.get_main_option("sqlalchemy.url")
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        compare_type=True,
    )
    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations against a live database connection."""
    if database_url:
        connectable = create_engine(database_url, poolclass=pool.NullPool)
    else:
        connectable = engine_from_config(
            config.get_section(config.config_ini_section, {}),
            prefix="sqlalchemy.",
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
