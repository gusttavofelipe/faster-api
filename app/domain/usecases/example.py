"""app/domain/usecases/example.py"""

from collections.abc import Generator, Iterator
from itertools import chain
from timeit import default_timer
from typing import Annotated, Any

from asyncpg.exceptions import PostgresError
from fastapi import Depends, Request
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.core.exceptions.db import (
	DBOperationError,
	ObjectAlreadyExistError,
	ObjectNotFound,
)
from app.core.i18n.manager import _
from app.core.logging import logger
from app.domain.models.example import ExampleModel
from app.domain.schemas.bulk_insert import BulkInsertCreate, BulkInsertResponse
from app.domain.schemas.collection_reponse import CollectionResponse
from app.domain.schemas.example import (
	ExampleCollectionOut,
	ExampleCreate,
	ExampleQueryParams,
	ExampleResponse,
	ExampleUpdate,
)
from app.infra.repositories.example import ExampleRepositoryDependency


class ExampleUsecase:
	"""Handles business logic for example table."""

	def __init__(self, example_repository: ExampleRepositoryDependency) -> None:
		"""Initializes the usecase with example repository.

		Args:
		    example_repository (ExampleRepositoryDependency):
				Repository for accessing example data.
		"""
		self.example_repository = example_repository

	async def get(self, id: UUID4) -> ExampleResponse:
		method_path: str = "ExampleUsecase.get"
		try:
			example_model: ExampleModel | None = await self.example_repository.get(
				filters={"id": id}
			)  # type: ignore
			if not example_model:
				raise ObjectNotFound
			return ExampleResponse.model_validate(example_model)
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"{_("SQLAlchemy error occurred")} in {method_path}: {exc}"
			)

	async def query(
		self, query_params: ExampleQueryParams, request: Request
	) -> CollectionResponse[ExampleResponse]:
		"""Executes a query to retrieve examples based on the provided parameters."""

		method_path: str = "ExampleUsecase.query"
		filter_params = query_params.model_dump(exclude_none=True)
		try:
			example_models: list[ExampleModel] = await self.example_repository.query(
				filter_params=filter_params,
			)  # type: ignore
			examples_response: list[ExampleResponse] = (
				ExampleCollectionOut.validate_python(example_models)
			)
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)
		return CollectionResponse[ExampleResponse].parse_collection(
			request=request,
			results=examples_response,
			query_params=query_params,
			count=len(examples_response),
		)

	async def create(self, data: ExampleCreate) -> ExampleResponse:
		method_path: str = "ExampleUsecase.create"
		try:
			async with self.example_repository.transaction() as transaction:
				example_model: ExampleModel = ExampleModel(**data.model_dump())
				await self.example_repository.create(
					orm_model=example_model,
					transaction=transaction,  # type: ignore
				)
				await transaction.flush()
				return ExampleResponse.model_validate(example_model)
		except IntegrityError:
			raise ObjectAlreadyExistError
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)

	async def bulk_insert(
		self, data: BulkInsertCreate[ExampleCreate]
	) -> BulkInsertResponse:
		method_path: str = "ExampleUsecase.bulk_insert"

		start: float = default_timer()
		it: Iterator[ExampleCreate] = iter(data.items)
		first_dict: dict[str, Any] = next(it).model_dump()
		columns: list[str] = list(first_dict.keys())

		rest_gen: Generator[dict[str, Any]] = (item.model_dump() for item in it)
		prepared_data_iter: Iterator[dict[str, Any]] = chain([first_dict], rest_gen)

		try:
			logger.info("Performing bulk insert...")
			await self.example_repository.bulk_insert_copy(
				table=self.example_repository.orm_model.__tablename__,
				columns=columns,
				data=prepared_data_iter,
			)
			end: float = default_timer()
			elapsed_time: float = end - start
			logger.info(f"Bulk insert finished. Elapsed time: {elapsed_time}")

			# FUTURE: to use a worker for scheduling this
			# task and change response schema
			return BulkInsertResponse(elapsed_time=elapsed_time)
		except (SQLAlchemyError, PostgresError) as exc:
			error_type: str = (
				"SQLAlchemy" if isinstance(exc, SQLAlchemyError) else "Postgres"
			)
			raise DBOperationError(
				message=f"{error_type} error occurred in {method_path}: {exc}"
			)

	async def partial_update(self, data: ExampleUpdate, id: UUID4) -> ExampleResponse:
		method_path: str = "ExampleUsecase.partial_update"
		try:
			async with self.example_repository.transaction() as transaction:
				example_model: ExampleModel | None = (
					await self.example_repository.partial_update(
						filters={"id": id},
						data=data.model_dump(),
						transaction=transaction,
					)  # type: ignore
				)
				if not example_model:
					raise ObjectNotFound
				return ExampleResponse.model_validate(example_model)
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)

	async def delete(self, id: UUID4) -> None:
		method_path: str = "ExampleUsecase.delete"
		try:
			async with self.example_repository.transaction() as transaction:
				example_model: ExampleModel | None = await self.example_repository.get(
					filters={"id": id}, transaction=transaction
				)  # type: ignore
				if not example_model:
					raise ObjectNotFound
				await self.example_repository.delete(
					orm_model=example_model,  # type: ignore
					transaction=transaction,
				)
		except SQLAlchemyError as exc:
			raise DBOperationError(
				message=f"SQLAlchemy error occurred in {method_path}: {exc}"
			)


ExampleUsecaseDependency = Annotated[ExampleUsecase, Depends()]
