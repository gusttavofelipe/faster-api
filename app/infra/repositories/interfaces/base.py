from typing import Any
from app.domain.models.base import DeclarativeBaseModel
from abc import ABC, abstractmethod


class Repository[OrmModelT: DeclarativeBaseModel](ABC):
    @abstractmethod
    async def create(self, model: OrmModelT) -> OrmModelT:
        ...

    @abstractmethod
    async def get(self, filter: dict[str, Any]) -> OrmModelT:
        ...

    @abstractmethod
    async def query(self, filter_params: dict[str, Any]) -> list[OrmModelT]:
        ...

    @abstractmethod
    async def partial_update(self, filter: dict[str, Any]) -> OrmModelT:
        ...

    @abstractmethod
    async def delete(self, filter: dict[str, Any]) -> None:
        ...
