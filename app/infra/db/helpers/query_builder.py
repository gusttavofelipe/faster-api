from typing import Any
 
from sqlalchemy.future import select
from sqlalchemy.sql.elements import BinaryExpression
from sqlalchemy.sql.selectable import Select
 
from app.domain.models.base import DeclarativeBaseModel
 
 
def apply_operator[OrmModelT: DeclarativeBaseModel](
    orm_model: type[OrmModelT], field: str, value: Any
) -> Any:
    """Create a SQLAlchemy filter expression based on field and value.
 
    Args:
        orm_model (OrmModelT):
            The SQLAlchemy ORM model class to get the column attribute from.
        field (str): The name of the model attribute (column) to filter on.
        value (Any):
            The value(s) to filter by. Can be a single value for equality or
            a dictionary like `{"in": [...]}` for 'IN' clauses.
 
    Returns:
        BinaryExpression:
        A SQLAlchemy expression representing the filter condition
        (e.g., `Model.field == value` or `Model.field IN [...]`).
    """
    if isinstance(value, dict):
        if "in" in value.keys():
            return getattr(orm_model, field).in_(value["in"])
 
    return getattr(orm_model, field) == value
 
 
def build_query[OrmModelT: DeclarativeBaseModel](
    orm_model: type[OrmModelT],
    filter: dict[str, Any] | None = None,
) -> Select[Any]:
    """Build a basic SQLAlchemy SELECT query for a given model with optional filters.
 
    Args:
        orm_model (OrmModelT):
            The SQLAlchemy ORM model class to query.
        filter (dict[str, Any] | None, optional):
            A dictionary of filters to apply.
            Keys are attribute names, values are filter values
            (matching apply_operator expectations). Defaults to None.
 
    Returns:
        Select: The constructed SQLAlchemy SELECT query object.
    """
    filter_: dict[str, Any] = filter or {}
    criteria: tuple[BinaryExpression[Any], ...] = tuple(
        apply_operator(orm_model, key, value) for key, value in filter_.items()
    )
    query: Select[Any] = select(orm_model).filter(*criteria)
 
    return query
