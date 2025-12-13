from pydantic import Field, NonNegativeInt, TypeAdapter

from app.domain.schemas.base import BaseSchema, OutSchema
from app.domain.schemas.query_params import BaseQueryParams


class ExampleBase(BaseSchema):
	"""Represents the base fields for the `example` moldel."""

	name: str | None = Field(
		default=None,
		min_length=3,
		max_length=60,
		description="Name",
		examples=["Gustavo"],
	)
	age: NonNegativeInt | None = Field(
		default=None, lt=117, description="Age", examples=[20]
	)


class ExampleCreate(ExampleBase): ...


class ExampleUpdate(ExampleBase): ...


class ExampleResponse(ExampleBase, OutSchema): ...


class ExampleQueryParams(BaseQueryParams, ExampleBase): ...


ExampleCollectionOut: TypeAdapter[list[ExampleResponse]] = TypeAdapter(
	list[ExampleResponse]
)
