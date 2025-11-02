from pydantic import UUID4
from app.domain.schemas.bulk_insert import BulkInsertCreate, BulkInsertResponse
from app.domain.usecases.example import ExampleUsecaseDependency
from app.domain.schemas.example import (
    ExampleCreate,
    ExampleQueryParams,
    ExampleResponse,
    ExampleUpdate,
)
from fastapi import APIRouter, Depends, Request, status
from app.domain.schemas.collection_reponse import CollectionResponse


router: APIRouter = APIRouter(prefix="/example", tags=["examples"])


@router.get(
    "/{id}",
    response_model=ExampleResponse,
    status_code=status.HTTP_200_OK,
    summary="Retrieve a single resource",
    response_description="Resource data found",
)
async def get(id: UUID4, usecase: ExampleUsecaseDependency) -> ExampleResponse:
    """
    Retrieve a single resource by its unique ID.

    - **id**: UUID of the resource
    - **Returns**: The resource data if found,
    otherwise triggers ObjectNotFound exception
    """
    return await usecase.get(id=id)


@router.get(
    "/",
    response_model=CollectionResponse[ExampleResponse],
    status_code=status.HTTP_200_OK,
    summary="Retrieve a list of resources",
    response_description="A paginated collection of resources",
)
async def query(
    request: Request,
    usecase: ExampleUsecaseDependency,
    query_params: ExampleQueryParams = Depends(),
) -> CollectionResponse[ExampleResponse]:
    """
    Retrieve a collection of resources filtered by optional query parameters.

    - **query_params**: Optional filters for the search
    - **Returns**: A paginated collection of resources matching the filters
    """
    return await usecase.query(request=request, query_params=query_params)


@router.post(
    "/",
    response_model=ExampleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create a new resource",
    response_description="The newly created resource",
)
async def create(
    usecase: ExampleUsecaseDependency, data: ExampleCreate
) -> ExampleResponse:
    """
    Create a new resource with the provided data.

    - **data**: Resource data required for creation
    - **Returns**: The newly created resource
    """
    return await usecase.create(data=data)


@router.post(
    "/bulk_insert",
    response_model=BulkInsertResponse,
    status_code=status.HTTP_200_OK,
    summary="Insert multiple resources in bulk",
    response_description="The newly created resource",
)
async def bulk_insert(
    usecase: ExampleUsecaseDependency, data: BulkInsertCreate[ExampleCreate]
) -> BulkInsertResponse:
    """
    Insert multiple resources in bulk with the provided data.

    - **data**: List of resource data to be inserted
    - **Returns**: The list of newly created resources
    """
    return await usecase.bulk_insert(data=data)


@router.patch(
    "/{id}",
    response_model=ExampleResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Partially update a resource",
    response_description="The updated resource",
)
async def partial_update(
    usecase: ExampleUsecaseDependency, data: ExampleUpdate, id: UUID4
) -> ExampleResponse:
    """
    Partially update fields of an existing resource by ID.

    - **id**: UUID of the resource to update
    - **data**: Fields to update
    - **Returns**: The updated resource
    """
    return await usecase.partial_update(data=data, id=id)


@router.delete(
    "/{id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete a resource",
    response_description="No content on successful deletion",
)
async def delete(id: UUID4, usecase: ExampleUsecaseDependency) -> None:
    """
    Delete a resource by its unique ID.

    - **id**: UUID of the resource to delete
    - **Returns**: No content (204) on successful deletion
    """
    await usecase.delete(id=id)
