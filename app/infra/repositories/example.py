from fastapi.param_functions import Depends
from app.domain.models.example import ExampleModel
from app.infra.repositories.postgres.base import PostgresRepository
from app.infra.db.manager import DatabaseDependency
from typing import Annotated, Type


class ExampleRepository(PostgresRepository[ExampleModel]):
    orm_model: Type[ExampleModel] = ExampleModel

    def __init__(self, session: DatabaseDependency) -> None:
        super().__init__(session=session)


ExampleRepositoryDependency = Annotated[ExampleRepository, Depends()]
