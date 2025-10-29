from app.infra.db.transaction import Transaction
from app.core.exceptions.db import ObjectNotFound
from typing import Any, Sequence

from sqlalchemy import update as sql_update
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.selectable import Select

from app.infra.db.helpers.query_builder import build_query
from app.domain.models.base import DeclarativeBaseModel
from app.infra.repositories.interfaces.base import Repository
from typing import Type


class PostgresRepository[OrmModelT: DeclarativeBaseModel](Repository[OrmModelT]):
    """Generic repository for PostgreSQL database operations using SQLAlchemy."""

    orm_model: Type[OrmModelT]

    def __init__(self, session: AsyncSession) -> None:
        """Initializes the repository with a database session."""

        self.session: AsyncSession = session

    def transaction(self) -> Transaction[OrmModelT]:
        """Creates a new transaction context."""

        return Transaction(session=self.session)

    async def create(
        self, orm_model: OrmModelT,
        transaction: Transaction[OrmModelT]
    ) -> OrmModelT:
        """Creates a new record in the database."""

        transaction.insert(orm_model=orm_model)
        return orm_model

    async def create_all(
        self,
        orm_models: list[OrmModelT],
        transaction: Transaction[OrmModelT]
    ) -> None:
        """Creates multiple ORM model records within a transactional context."""

        transaction.insert_all(orm_models=orm_models)
        await transaction.session.flush()

    async def get(
        self,
        filters: dict[str, Any],
        transaction: Transaction[OrmModelT]
    ) -> OrmModelT | None:
        """Retrieves a single record based on the provided filters."""

        query: Select[Any] = build_query(orm_model=self.orm_model, filter=filters)
        data: OrmModelT | None = (await transaction.session.execute(query)).scalars().first()
        return data

    async def query(
        self, filter_params: dict[str, Any],
        transaction: Transaction[OrmModelT]
    ) -> list[OrmModelT]:
        """Retrieves a list of records based on query parameters."""

        limit = filter_params.pop("limit", 10)
        offset = filter_params.pop("offset", 0)

        query: Select[Any] = build_query(orm_model=self.orm_model, filter=filter_params)

        if limit is not None:
            query = query.limit(limit)

        if offset is not None:
            query = query.offset(offset)

        data: Sequence[OrmModelT] = (await transaction.session.execute(query)).scalars().all()

        return list(data)

    async def partial_update(
        self,
        filters: dict[str, Any],
        data: dict[str, Any],
        transaction: Transaction[OrmModelT]
    ) -> None:
        """Partially update records matching filters with the provided data.

        Supported operators:
            - __eq (default if no operator)
            - __ne  (not equal)
            - __lt  (less than)
            - __lte (less or equal)
            - __gt  (greater than)
            - __gte (greater or equal)
            - __in (value must be a list/tuple)

        Args:
            filters (dict[str, Any]):
             Dict of column names and values to filter the target records.
            data( dict[str, Any]):
                Dict of column names and new values to update those records.
        """

        conditions = []

        for key, value in filters.items():
            if "__" in key:
                col_name, op = key.split("__", 1)
            else:
                col_name, op = key, "eq"

            column = getattr(self.orm_model, col_name)

            if op == "eq":
                conditions.append(column == value)
            elif op == "ne":
                conditions.append(column != value)
            elif op == "lt":
                conditions.append(column < value)
            elif op == "lte":
                conditions.append(column <= value)
            elif op == "gt":
                conditions.append(column > value)
            elif op == "gte":
                conditions.append(column >= value)
            elif op == "in":
                conditions.append(column.in_(value))
            else:
                raise ValueError(f"Unsupported operator: {op}")

        stmt = (
            sql_update(self.orm_model)
            .where(*conditions)
            .values(**data)
            .execution_options(synchronize_session="fetch")
        )

        await transaction.session.execute(stmt)

    async def delete(
        self: "PostgresRepository", filter: dict, transaction: Transaction
    ) -> None:
        """Remove a given ORM model instance from the database."""

        instance = await self.get(filters=filter, transaction=transaction)
        if not instance:
            raise ObjectNotFound

        await transaction.session.delete(instance)
