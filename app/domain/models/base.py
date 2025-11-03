from typing import Any
from sqlalchemy import DateTime
from uuid import uuid4
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm._orm_constructors import mapped_column
from uuid import UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, UTC
from sqlalchemy import func


class DeclarativeBaseModel(DeclarativeBase):
    ...


def get_utc_now():
    return datetime.now(UTC)


class CreateBaseModel(DeclarativeBaseModel):
    __abstract__ = True

    pk_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), server_default=func.gen_random_uuid(), nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        nullable=False, 
        server_default=func.now()
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
