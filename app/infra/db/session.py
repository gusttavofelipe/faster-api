from typing import AsyncGenerator, Annotated
from functools import lru_cache

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from fastapi import Depends
from app.core.config import settings


@lru_cache(maxsize=1)
def get_engine() -> AsyncEngine:
    return create_async_engine(
        settings.DATABASE_URL,
        echo=False,
        pool_pre_ping=True,
        pool_size=20,
        pool_recycle=1800,
        max_overflow=40,
        future=True,
    )


@lru_cache(maxsize=1)
def get_sessionmaker() -> async_sessionmaker[AsyncSession]:
    return async_sessionmaker(
        bind=get_engine(),
        expire_on_commit=False,
        class_=AsyncSession,
    )


async def get_session() -> AsyncGenerator[AsyncSession, None]:
    session = get_sessionmaker()()
    try:
        yield session
    except Exception:
        await session.rollback()
        raise
    finally:
        await session.close()


DatabaseDependency = Annotated[AsyncSession, Depends(get_session)]
