from app.domain.usecases.example import ExampleUsecaseDependency
from app.core.exceptions.db import DBOperationError, ObjectAlreadyExistError
from app.domain.schemas.example import (
    ExampleCreate, ExampleQueryParams, ExampleResponse
)
from fastapi import APIRouter, Depends, HTTPException, Request, status
from app.domain.schemas.collection_reponse import CollectionResponse


router: APIRouter = APIRouter(prefix="/example", tags=["example"])

@router.get(
    "/",
    response_model=CollectionResponse[ExampleResponse],
    status_code=status.HTTP_200_OK
)
async def query(
    request: Request,
    usecase: ExampleUsecaseDependency,
    query_params: ExampleQueryParams = Depends()
) -> CollectionResponse[ExampleResponse]:
    try:
        return await usecase.query(request=request, query_params=query_params)
    except DBOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message
        )


@router.post("/", response_model=ExampleResponse, status_code=status.HTTP_201_CREATED)
async def create(
    usecase: ExampleUsecaseDependency,
    data: ExampleCreate
) -> ExampleResponse:
    try:
        return await usecase.create(data=data)
    except ObjectAlreadyExistError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=exc.message)
    except DBOperationError as exc:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail=exc.message
        )
