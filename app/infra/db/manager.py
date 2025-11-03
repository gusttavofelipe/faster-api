from sqlalchemy import text
from typing import AsyncGenerator, Annotated

from sqlalchemy.ext.asyncio import (
    AsyncSession,
    AsyncEngine,
    async_sessionmaker,
    create_async_engine,
)
from fastapi import Depends
from app.core.config import settings
from asyncpg import Pool, create_pool


class DatabaseManager:
    _engine: AsyncEngine | None = None
    _sessionmaker: async_sessionmaker[AsyncSession] | None = None
    _pool: Pool | None = None

    @classmethod
    def get_engine(cls) -> AsyncEngine:
        if cls._engine is None:
            cls._engine = create_async_engine(
                settings.DATABASE_URL,
                echo=False,
                pool_pre_ping=True,
                pool_size=20,
                max_overflow=40,
                pool_recycle=1800,
                future=True,
            )
        return cls._engine

    @classmethod
    def get_sessionmaker(cls) -> async_sessionmaker[AsyncSession]:
        if cls._sessionmaker is None:
            cls._sessionmaker = async_sessionmaker(
                bind=cls.get_engine(),
                expire_on_commit=False,
                class_=AsyncSession,
            )
        return cls._sessionmaker

    @classmethod
    async def get_session(cls) -> AsyncGenerator[AsyncSession, None]:
        yield cls.get_sessionmaker()()

    @classmethod
    async def get_asyncpg_pool(cls) -> Pool:
        if cls._pool is None:
            dsn: str = settings.DATABASE_URL.replace("+asyncpg", "")
            cls._pool = await create_pool(dsn=dsn, min_size=5, max_size=20)
            # increase to min_size=10, max_size=50 if it's to insert millions
        return cls._pool  # type: ignore

    @classmethod
    async def test_connection(cls) -> bool:
        session: AsyncSession = await anext(cls.get_session())
        await session.execute(text("SELECT 1"))
        await session.close()
        return True


DatabaseDependency = Annotated[AsyncSession, Depends(DatabaseManager.get_session)]
