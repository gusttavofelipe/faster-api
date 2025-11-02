from app.domain.models.base import CreateBaseModel
from sqlalchemy import Integer, String
from sqlalchemy.orm import Mapped, mapped_column


class ExampleModel(CreateBaseModel):
    __tablename__: str = "example"

    name: Mapped[str | None] = mapped_column(String, nullable=True)
    age: Mapped[int | None] = mapped_column(Integer, nullable=True)
