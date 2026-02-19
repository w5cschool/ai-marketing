from collections.abc import AsyncGenerator

from fastapi import Header
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db_session


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async for session in get_db_session():
        yield session


async def get_user_id(x_user_id: str | None = Header(default=None)) -> str:
    return x_user_id or "anonymous"
