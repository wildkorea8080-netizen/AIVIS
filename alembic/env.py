import asyncio
from logging.config import fileConfig

from sqlalchemy import pool
from sqlalchemy.ext.asyncio import async_engine_from_config

from alembic import context

# ORM 모델을 임포트해야 autogenerate가 테이블을 인식한다
from app.models.orm import Base  # noqa: F401 — side-effect import
from app.config import settings

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)

target_metadata = Base.metadata

# DATABASE_URL을 .env에서 주입 (alembic.ini의 sqlalchemy.url 덮어쓰기)
def _async_url() -> tuple[str, dict]:
    from app.db import _to_asyncpg_url
    return _to_asyncpg_url(settings.database_url)


def run_migrations_offline() -> None:
    url = _async_url()
    context.configure(
        url=url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )
    with context.begin_transaction():
        context.run_migrations()


def do_run_migrations(connection):
    context.configure(connection=connection, target_metadata=target_metadata)
    with context.begin_transaction():
        context.run_migrations()


async def run_async_migrations() -> None:
    from sqlalchemy.ext.asyncio import create_async_engine

    clean_url, connect_args = _async_url()
    connectable = create_async_engine(clean_url, connect_args=connect_args, poolclass=pool.NullPool)
    async with connectable.connect() as connection:
        await connection.run_sync(do_run_migrations)
    await connectable.dispose()


def run_migrations_online() -> None:
    asyncio.run(run_async_migrations())


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
