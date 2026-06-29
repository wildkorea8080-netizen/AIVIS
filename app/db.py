from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase

from app.config import settings


def _to_asyncpg_url(url: str) -> tuple[str, dict]:
    """postgresql:// → postgresql+asyncpg://, 쿼리 파라미터 제거 후 connect_args 반환."""
    from urllib.parse import urlparse, urlencode, parse_qs, urlunparse

    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "postgresql+asyncpg://", 1)

    parsed = urlparse(url)
    params = parse_qs(parsed.query)

    # asyncpg가 이해 못하는 파라미터는 모두 제거하고 SSL만 connect_args로 전달
    sslmode = params.get("sslmode", ["disable"])[0]
    use_ssl = sslmode in ("require", "verify-ca", "verify-full", "prefer")

    clean_url = urlunparse(parsed._replace(query=""))
    connect_args = {"ssl": use_ssl} if use_ssl else {}
    return clean_url, connect_args


def _make_engine():
    url = settings.database_url
    if not url:
        return None
    clean_url, connect_args = _to_asyncpg_url(url)
    return create_async_engine(clean_url, connect_args=connect_args, pool_pre_ping=True, echo=False)


engine = _make_engine()

AsyncSessionLocal: async_sessionmaker[AsyncSession] | None = (
    async_sessionmaker(engine, expire_on_commit=False) if engine else None
)


class Base(DeclarativeBase):
    pass


async def get_db():
    if AsyncSessionLocal is None:
        yield None
        return
    async with AsyncSessionLocal() as session:
        yield session
