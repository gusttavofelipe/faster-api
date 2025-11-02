from datetime import datetime
from typing import ClassVar
from pydantic import BaseModel, ConfigDict, Field, UUID4


class BaseSchema(BaseModel):
    model_config: ClassVar[ConfigDict] = ConfigDict(from_attributes=True)


class OutSchema(BaseSchema):
    id: UUID4 = Field()
    created_at: datetime = Field()
    updated_at: datetime = Field()
