from typing import Annotated

from fastapi.param_functions import Depends

from app.domain.models.example import ExampleModel
from app.infra.db.manager import DatabaseDependency
from app.infra.repositories.postgres.base import PostgresRepository


class ExampleRepository(PostgresRepository[ExampleModel]):
	orm_model: type[ExampleModel] = ExampleModel

	def __init__(self, session: DatabaseDependency) -> None:
		super().__init__(session=session)


ExampleRepositoryDependency = Annotated[ExampleRepository, Depends()]
