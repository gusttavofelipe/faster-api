from app.infra.db.transaction import Transaction
from typing import Any
from app.domain.models.base import DeclarativeBaseModel
from abc import ABC, abstractmethod


class Repository[OrmModelT: DeclarativeBaseModel](ABC):
    @abstractmethod
    async def create(
        self,
        orm_model: OrmModelT,
        transaction: Transaction[OrmModelT]
    ) -> OrmModelT:
        ...

    @abstractmethod
    async def get(
        self,
        filters: dict[str, Any],
        transaction: Transaction[OrmModelT]
    ) -> OrmModelT | None:
        ...

    @abstractmethod
    async def query(
        self,
        filter_params: dict[str, Any],
    ) -> list[OrmModelT]:
        ...

    @abstractmethod
    async def partial_update(
        self,
        filters: dict[str, Any],
        data: dict[str, Any],
        transaction: Transaction[OrmModelT]
    ) -> OrmModelT | None:
        ...

    @abstractmethod
    async def delete(
        self,
        orm_model: OrmModelT,
        transaction: Transaction[OrmModelT]
    ) -> None:
        ...
