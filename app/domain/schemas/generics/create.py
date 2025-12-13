from pydantic import NonNegativeInt

from app.domain.schemas.base import BaseSchema


class CreateSchema[SchemaT: BaseSchema](BaseSchema):
	event: str
	version: NonNegativeInt
	data: SchemaT
