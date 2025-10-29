from sqlalchemy.exc import IntegrityError
from app.core.exceptions.db import ObjectAlreadyExistError
from sqlalchemy.exc import SQLAlchemyError
from typing import Annotated
from fastapi import Depends, Request

from app.core.exceptions.db import DatabaseConnectionError, DBOperationError
from app.domain.models.example import ExampleModel
from app.infra.repositories.example import ExampleRepositoryDependency
from app.domain.schemas.collection_reponse import CollectionResponse
from app.domain.schemas.example import (
    ExampleCollectionOut,
    ExampleCreate,
    ExampleResponse,
    ExampleQueryParams,
)


class ExampleUsecase:
    """Handles business logic for example table."""

    def __init__(
        self, example_repository: ExampleRepositoryDependency
    ) -> None:
        """Initializes the usecase with example repository.

        Args:
            example_repository (ExampleRepositoryDependency):
                Repository for accessing example data.
        """
        self.example_repository = example_repository

    async def query(
        self, query_params: ExampleQueryParams, request: Request
    ) -> CollectionResponse[ExampleResponse]:
        """Executes a query to retrieve examples based on the provided parameters.

        Args:
            query_params (QueryParams):
                Parameters to filter the query. request (Request): The HTTP request context.

        Raises:
            DBOperationError: When there is a database operation failure.
            Exception: For other unexpected database or SQL errors.

        Returns:
            CollectionResponse[ExampleResponse]:
                Paginated response with the examples.
        """

        method_path: str = "ExampleUsecase.query"
        try:
            async with self.example_repository.transaction() as transaction:
                example_models: list[
                    ExampleModel
                ] = await self.example_repository.query(
                    filter_params=query_params.model_dump(exclude_none=True),
                    transaction=transaction
                ) # type: ignore
                examples_response: list[ExampleResponse] = (
                    ExampleCollectionOut.validate_python(example_models)
                )

        except DatabaseConnectionError as exc:
            raise DBOperationError(
                message=f"DB Connection occurred error in {method_path}: {exc.message}"
            )
        except SQLAlchemyError as exc:
            raise DBOperationError(
                message=f"SQLAlchemy error occurred in {method_path}: {exc}"
            )
        except Exception as exc:
            raise DBOperationError(
                message=f"Unexpected error occurred in {method_path}: {exc}"
            )

        return CollectionResponse.parse_collection(
            request=request,
            results=examples_response,
            query_params=query_params,
            count=len(examples_response),
        )


    async def create(self, data: ExampleCreate) -> ExampleResponse:
        method_path: str = "ExampleUsecase.create"
        try:
            async with self.example_repository.transaction() as transaction:

                example_model = ExampleModel(**data.model_dump())
                await self.example_repository.create(
                    orm_model=example_model, transaction=transaction # type: ignore
                )
                return ExampleResponse.model_validate(example_model)
        except DatabaseConnectionError as exc:
            raise DBOperationError(
                message=f"DB Connection occurred error in {method_path}: {exc.message}"
            )
        except IntegrityError as exc:
            raise ObjectAlreadyExistError

        except SQLAlchemyError as exc:
            raise DBOperationError(
                message=f"SQLAlchemy error occurred in {method_path}: {exc}"
            ) from exc
        except Exception as exc:
            raise DBOperationError(
                message=f"Unexpected error occurred in {method_path}: {exc}"
            ) from exc

ExampleUsecaseDependency = Annotated[ExampleUsecase, Depends()]
