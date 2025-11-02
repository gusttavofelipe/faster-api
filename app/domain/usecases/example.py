from typing import Any
from timeit import default_timer
from pydantic import UUID4
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.core.exceptions.db import (
    ObjectAlreadyExistError,
    ObjectNotFound,
    DBOperationError,
)
from typing import Annotated
from fastapi import Depends, Request

from app.domain.models.base import ensure_defaults
from app.domain.models.example import ExampleModel
from app.domain.schemas.bulk_insert import BulkInsertCreate, BulkInsertResponse
from app.infra.repositories.example import ExampleRepositoryDependency
from app.domain.schemas.collection_reponse import CollectionResponse
from app.domain.schemas.example import (
    ExampleCollectionOut,
    ExampleCreate,
    ExampleResponse,
    ExampleQueryParams,
    ExampleUpdate,
)


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
                message=f"SQLAlchemy error occurred in {method_path}: {exc}"
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
            examples_response: list[
                ExampleResponse
            ] = ExampleCollectionOut.validate_python(example_models)
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
                    orm_model=example_model, transaction=transaction  # type: ignore
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
        prepared_data: list[dict[str, Any]] = [item.model_dump() for item in data.items]
        ensure_defaults(data=prepared_data)
        columns: list[str] = list(prepared_data[0].keys())

        try:
            await self.example_repository.bulk_insert_copy(
                table=self.example_repository.orm_model.__tablename__,
                columns=columns,
                data=prepared_data,
            )
        except SQLAlchemyError as exc:
            raise DBOperationError(
                message=f"SQLAlchemy error occurred in {method_path}: {exc}"
            )
        end: float = default_timer()

        # FUTURE: to use a worker for scheduling this
        # task and change response schema
        return BulkInsertResponse(
            inserted_rows=len(prepared_data), elapsed_time=end - start
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
                    orm_model=example_model, transaction=transaction  # type: ignore
                )
        except SQLAlchemyError as exc:
            raise DBOperationError(
                message=f"SQLAlchemy error occurred in {method_path}: {exc}"
            )


ExampleUsecaseDependency = Annotated[ExampleUsecase, Depends()]
