from collections.abc import AsyncGenerator
from urllib.parse import parse_qsl, urlencode, urlparse, urlunparse

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.config import get_settings

settings = get_settings()


def _normalize_database_url(url: str) -> str:
    """Normalize asyncpg URL query params (e.g. sslmode -> ssl)."""
    if not url.startswith("postgresql+asyncpg://"):
        return url

    parsed = urlparse(url)
    if not parsed.query:
        return url

    query_items = parse_qsl(parsed.query, keep_blank_values=True)
    updated_items: list[tuple[str, str]] = []
    for key, value in query_items:
        if key == "sslmode":
            updated_items.append(("ssl", value))
        else:
            updated_items.append((key, value))

    normalized_query = urlencode(updated_items, doseq=True)
    return urlunparse(parsed._replace(query=normalized_query))


class Base(DeclarativeBase):
    pass


engine = create_async_engine(_normalize_database_url(settings.database_url), echo=settings.debug, future=True)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)


async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    async with AsyncSessionLocal() as session:
        yield session
