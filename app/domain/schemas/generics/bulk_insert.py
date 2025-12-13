from pydantic import Field

from app.domain.schemas.base import BaseSchema


class BulkInsertCreate[SchemaT: BaseSchema](BaseSchema):
	"""Generic schema for bulk inserts of any Pydantic model."""

	items: list[SchemaT] = Field(
		...,
		description="List of records to insert in bulk.",
		examples=[
			[
				{"name": "felipe", "age": 19},
				{"name": "gustavo", "age": 20},
			]
		],
	)


class BulkInsertResponse(BaseSchema):
	# inserted_rows: int = Field(
	#     ..., description="Number of inserted rows", examples=[324]
	# )
	elapsed_time: float = Field(
		..., description="Time spent for insertion", examples=[32.14]
	)
