from fastapi import Query
from pydantic import BaseModel, NonNegativeInt
 
 
class QueryParams(BaseModel):
    """Schema for standard pagination query parameters.
 
    Defines the structure for 'offset' and 'limit' used in API requests for pagination.
 
    Args:
        offset (NonNegativeInt | None):
            Number of records to skip from the beginning of the result set. Defaults to 0.
            limit (NonNegativeInt | None): Maximum number of records to return
            in a single response. Defaults to 100.
    """
 
    offset: NonNegativeInt | None = Query(
        0, description="Number of data to offset for pagination", exclude=True
    )
    limit: NonNegativeInt | None = Query(
        10, description="Maximum number of data to return", exclude=True
    )
 