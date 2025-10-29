from fastapi import Query
from app.domain.schemas.query_params import QueryParams
from pydantic import Field, TypeAdapter
from app.domain.schemas.base import BaseSchema


class ExampleBase(BaseSchema):
    """Represents the base fields for a example.

    Args:
        BaseSchema (BaseSchema):
            Schema base class providing validation and commom functionality
    """

    field: str = Field(description="Example of description", examples=["example1"])
    field2: str | None = Field(
        None,
        description="Example of description",
        examples=["example1"]
    )

class ExampleCreate(ExampleBase):
    ...


class ExampleResponse(ExampleBase):
    ...


class ExampleQueryParams(QueryParams):
    field2: str | None = Query(
        None,
        description="Example of description",
        examples=["example2"]
    )


ExampleCollectionOut: TypeAdapter[list[ExampleResponse]] = TypeAdapter(
    list[ExampleResponse]
)
