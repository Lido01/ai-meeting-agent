from logging.config import fileConfig
import os

from sqlalchemy import engine_from_config, pool
from alembic import context

# ----------------------------------------------------
# 1. ALEMBIC & LOGGING CONFIGURATION
# ----------------------------------------------------

# This is the Alembic Config object, providing access to alembic.ini values.
config = context.config

# Interpret the config file for Python logging.
if config.config_file_name is not None:
    fileConfig(config.config_file_name)

# ----------------------------------------------------
# 2. MODEL METADATA IMPORT (For Autogenerate Support)
# ----------------------------------------------------

# Import your database Base and all models so Alembic detects your tables.
from app.database import Base, DATABASE_URL # <-- Imported DATABASE_URL to fix the driver bug
from app.models.user import User
from app.models.meeting import Meeting
from app.models.task import Task
from app.models.context_change import ContextChange

# Set target_metadata to enable 'alembic revision --autogenerate'
target_metadata = Base.metadata

# ----------------------------------------------------
# 3. HELPER FUNCTION TO GET REAL DATABASE URL
# ----------------------------------------------------

def get_database_url() -> str:
    """
    Determines the correct database URL.
    Prioritizes the live URL from app.database, falls back to environment 
    variables, and uses the alembic.ini config as a last resort.
    """
    # 1. Check if app.database exposes a live URL string
    if isinstance(DATABASE_URL, str) and "+driver" not in DATABASE_URL:
        return DATABASE_URL
        
    # 2. Check if a string version exists elsewhere in your local environment
    env_url = os.getenv("DATABASE_URL")
    if env_url and "+driver" not in env_url:
        return env_url
        
    # 3. Fallback to alembic.ini (Ensure you update the URL inside alembic.ini too!)
    return config.get_main_option("sqlalchemy.url")

# ----------------------------------------------------
# 4. MIGRATION RUN MODES
# ----------------------------------------------------

def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL instead of a live Engine.
    Emits raw SQL strings to the terminal/script output.
    """
    # Fetch the dynamically resolved connection string
    url = get_database_url()
    
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

    Creates a live database connection engine to execute migrations.
    """
    # Read the configuration dictionary from the alembic.ini section
    ini_section = config.get_section(config.config_ini_section, {})
    
    # Dynamically inject the real URL, replacing the broken "+driver" placeholder
    ini_section["sqlalchemy.url"] = get_database_url()

    # Create the connection engine using our updated runtime configuration
    connectable = engine_from_config(
        ini_section,
        prefix="sqlalchemy.",
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection, 
            target_metadata=target_metadata
        )

        with context.begin_transaction():
            context.run_migrations()

# ----------------------------------------------------
# 5. EXECUTION ROUTER
# ----------------------------------------------------

if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
