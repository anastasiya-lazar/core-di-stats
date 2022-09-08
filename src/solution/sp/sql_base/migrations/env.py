import asyncio
import os
import ssl

from logging.config import fileConfig

from alembic import context
from sqlalchemy import engine_from_config, pool
from sqlalchemy.ext.asyncio import AsyncEngine


# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config

# Interpret the config file for Python logging.
# This line sets up loggers basically.
fileConfig(config.config_file_name)

target_metadata = None


try:
    from solution.sp.sql_base.models import Base
    target_metadata = Base.metadata
except Exception as e:
    print(e)
    print("CUSTOM METADATA IS IGNORED")


def get_connection_string():
    db_endpoint = os.environ.get("DB_ENDPOINT", "")
    db_port = os.environ.get("DB_PORT", "3306")
    db_username = os.environ.get("DB_USERNAME", "")
    db_password = os.environ.get("DB_PASSWORD", "")
    db_name = os.environ.get("DB_NAME", "")
    db_user_host = os.environ.get("DB_USER_HOST", "")
    db_type = os.environ.get("DB_TYPE", "mysql")
    if db_user_host:
        db_username += f"@{db_user_host}"
    print("-----------------")
    print(config.get_section(config.config_ini_section))

    section = config.get_section(config.config_ini_section)
    return section["sqlalchemy.url"].format(db_username, db_password, db_endpoint, db_port, db_name)


def get_connect_args():
    args = {}
    db_ssl_path_cert = os.environ.get("DB_SSL_PATH_CERT", "")
    if db_ssl_path_cert:
        args['ssl'] = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH, capath=db_ssl_path_cert)
    return args


def run_migrations_offline():
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    url = get_connection_string()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
        connect_args=get_connect_args(),
    )

    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, compare_type=True, target_metadata=target_metadata)

    with context.begin_transaction():
        context.run_migrations()


async def run_migrations_online():
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context .

    """
    alembic_config = config.get_section(config.config_ini_section)
    alembic_config["sqlalchemy.url"] = get_connection_string()

    connectable = AsyncEngine(
        engine_from_config(
            alembic_config,
            prefix="sqlalchemy.",
            poolclass=pool.NullPool,
            future=True,
            connect_args=get_connect_args(),
        )
    )

    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)


if context.is_offline_mode():
    run_migrations_offline()
else:
    asyncio.run(run_migrations_online())
