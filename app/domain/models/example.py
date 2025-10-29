from sqlalchemy import String
from sqlalchemy.orm import Mapped, mapped_column
from app.domain.models.base import DeclarativeBaseModel


class ExampleModel(DeclarativeBaseModel):
    __tablename__ = "example"

    field: Mapped[str | None] = mapped_column(String, primary_key=True)
    field2: Mapped[str | None] = mapped_column(String, nullable=True)
