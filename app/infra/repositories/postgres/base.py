from collections.abc import AsyncGenerator, Generator, Iterable, Iterator, Sequence
from itertools import islice
from typing import Any

from asyncpg import Pool
from sqlalchemy import update as sql_update
from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.selectable import Select

from app.domain.models.base import DeclarativeBaseModel
from app.infra.db.helpers.query_builder import build_query
from app.infra.db.manager import DatabaseManager
from app.infra.db.transaction import Transaction
from app.infra.repositories.interfaces.base import Repository


class PostgresRepository[OrmModelT: DeclarativeBaseModel](Repository[OrmModelT]):
	"""Generic repository for PostgreSQL database operations using SQLAlchemy."""

	orm_model: type[OrmModelT]

	def __init__(self, session: AsyncSession) -> None:
		"""Initializes the repository with a database session."""

		self.session: AsyncSession = session

	def transaction(self) -> Transaction[OrmModelT]:
		"""Creates a new transaction context."""

		return Transaction[OrmModelT](session=self.session)

	async def create(
		self, orm_model: OrmModelT, transaction: Transaction[OrmModelT]
	) -> OrmModelT:
		"""Creates a new record in the database."""

		transaction.insert(orm_model=orm_model)
		return orm_model

	async def create_all(
		self, orm_models: list[OrmModelT], transaction: Transaction[OrmModelT]
	) -> None:
		"""Creates multiple ORM model records within a transactional context."""

		transaction.insert_all(orm_models=orm_models)
		await transaction.session.flush()

	async def bulk_insert_copy(
		self,
		table: str,
		columns: list[str],
		data: Iterable[dict[str, Any]],
		batch_size: int = 5000,
	) -> None:
		async def get_batches(
			iterable: Iterable[dict[str, Any]], size: int
		) -> AsyncGenerator[list[dict[str, Any]], None]:
			"""Generates batches of size `size` from any iterable."""

			it: Iterator[dict[str, Any]] = iter(iterable)
			while True:
				batch: list[dict[str, Any]] = list(islice(it, size))
				if not batch:
					break
				yield batch

		pool: Pool = await DatabaseManager.get_asyncpg_pool()

		async with pool.acquire() as connection:
			async for batch in get_batches(iterable=data, size=batch_size):
				records_gen: Generator[tuple[Any | None, ...]] = (
					tuple(record.get(col, None) for col in columns) for record in batch
				)
				await connection.copy_records_to_table(
					table_name=table,
					records=records_gen,
					columns=columns,
				)

	async def get(
		self, filters: dict[str, Any], transaction: Transaction[OrmModelT] | None = None
	) -> OrmModelT | None:
		"""Retrieves a single record based on the provided filters."""

		session: AsyncSession = transaction.session if transaction else self.session
		query: Select[tuple[OrmModelT]] = build_query(
			orm_model=self.orm_model, filter=filters
		)  # type: ignore
		data: OrmModelT | None = (await session.execute(query)).scalars().first()
		return data

	async def query(
		self,
		filter_params: dict[str, Any],
		transaction: Transaction[OrmModelT] | None = None,
	) -> list[OrmModelT]:
		"""Retrieves a list of records based on query parameters.

		Uses the session's automatic transaction management.
		No explicit transaction needed for simple reads.
		"""

		session: AsyncSession = transaction.session if transaction else self.session
		limit: int = filter_params.pop("limit", 10)
		offset: int = filter_params.pop("offset", 0)
		query: Select[tuple[OrmModelT]] = build_query(
			orm_model=self.orm_model, filter=filter_params
		)  # type: ignore
		if limit is not None:
			query = query.limit(limit)
		if offset is not None:
			query = query.offset(offset)

		data: Sequence[OrmModelT] = (await session.execute(query)).scalars().all()

		return list(data)

	async def partial_update(
		self,
		filters: dict[str, Any],
		data: dict[str, Any],
		transaction: Transaction[OrmModelT],
	) -> OrmModelT | None:
		"""Partially update records matching filters with the provided data."""

		conditions: list[BinaryExpression[Any]] = build_query(
			orm_model=self.orm_model, filter=filters, return_conditions=True
		)  # type: ignore

		stmt = (
			sql_update(self.orm_model)
			.where(*conditions)
			.values(**data)
			.execution_options(synchronize_session=False)
			.returning(self.orm_model)
		)

		result: Result[tuple[OrmModelT]] = await transaction.session.execute(stmt)
		return result.scalars().first()

	async def delete(
		self, orm_model: OrmModelT, transaction: Transaction[OrmModelT]
	) -> None:
		await transaction.session.delete(orm_model)
