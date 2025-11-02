from functools import lru_cache
from typing import Any
from sqlalchemy import DateTime
from uuid import uuid4
from sqlalchemy.orm.base import Mapped
from sqlalchemy.orm._orm_constructors import mapped_column
from uuid import UUID
from sqlalchemy.orm import DeclarativeBase
from sqlalchemy.dialects.postgresql import UUID as PG_UUID
from datetime import datetime, UTC


class DeclarativeBaseModel(DeclarativeBase):
    ...


@lru_cache
def get_utc_now():
    return datetime.now(UTC)


def ensure_defaults(data: list[dict[str, Any]]):
    """Ensure the default fields for the given records

    Args:
        data **list[dict[str, Any]**: list of dicts of records
    """

    # micro-optimization: fewer method lookups
    # Python needs to resolve, on each iteration:
    # 	1 - The type of 'row' (is it a dict, list...?):
    # 		When Python sees >>>row["id"] = value,
    # 		it doesn't automatically assume that 'row' is a dict
    # 	2 - Which __setitem__ method to use depending on the type of 'row'
    # 	3 - Execute the operation
    #
    # But if you do beforehand: >>>append = dict.__setitem
    # you "cache" this pointer to the method in the 'append' variable.
    # Then inside the loop, you only execute step 3 — without repeated lookup

    now = get_utc_now()
    append = dict.__setitem__

    for row in data:
        append(row, "id", uuid4())
        append(row, "created_at", now)
        append(row, "updated_at", now)


class CreateBaseModel(DeclarativeBaseModel):
    __abstract__ = True

    pk_id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    id: Mapped[UUID] = mapped_column(
        PG_UUID(as_uuid=True), default=uuid4, nullable=False
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=get_utc_now, nullable=False
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        default=get_utc_now,
        onupdate=get_utc_now,
        nullable=False,
    )
