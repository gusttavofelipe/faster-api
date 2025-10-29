from pydantic import BaseModel, Field


class HealthOut(BaseModel):
    status: str = Field(default="OK")
