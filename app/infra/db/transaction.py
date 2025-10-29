from collections.abc import Sequence
from types import TracebackType
from typing import Self

from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import logger
from app.domain.models.base import DeclarativeBaseModel


class Transaction[OrmModelT: DeclarativeBaseModel]:
    """Transaction manager with minimal overhead."""

    __slots__ = ("session", "_in_transaction")

    def __init__(self, session: AsyncSession) -> None:
        self.session = session
        self._in_transaction = False

    async def __aenter__(self) -> Self:
        """Starts a new transaction if one is not already active."""

        if not self.session.in_transaction():
            await self.session.begin()
            self._in_transaction = True
            logger.info("Transaction has begun")
        return self

    async def __aexit__(
        self,
        exc_t: type[BaseException] | None,
        exc_v: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        """Finalizes the transaction, committing or rolling back changes."""

        if not self._in_transaction:
            return

        try:
            if exc_v:
                logger.warning("Exception occurred within transaction, rolling back")
                await self.session.rollback()
            else:
                logger.info(f"Committing transaction on session")
                await self.session.commit()
        except SQLAlchemyError as exc:
            logger.error(f"Error during commit/rollback: {exc}")
            await self.session.rollback()
            raise
        finally:
            self._in_transaction = False

    def insert(self, orm_model: OrmModelT) -> OrmModelT:
        """Adds an ORM model to the session for insertion (sync operation)."""

        self.session.add(orm_model)
        return orm_model

    def insert_all(self, orm_models: Sequence[OrmModelT]) -> Sequence[OrmModelT]:
        """Adds multiple ORM models to the session for insertion (sync operation)."""

        self.session.add_all(orm_models)
        return orm_models

    async def flush(self) -> None:
        """Flush pending changes without committing the transaction."""

        await self.session.flush()

    async def refresh(self, orm_model: OrmModelT) -> OrmModelT:
        """Refresh an ORM model from the database."""

        await self.session.refresh(orm_model)
        return orm_model
