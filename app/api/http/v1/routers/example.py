from fastapi import APIRouter, status

from app.domain.schemas.example import (
	ExampleCreate,
)
from app.domain.schemas.generics.create import CreateSchema
from app.infra.kafka.producer import KafkaProducerDependency
from app.infra.kafka.topics import ExampleTopics

router: APIRouter = APIRouter(prefix="/example", tags=["examples"])


# @router.get(
# 	"/{id}",
# 	response_model=ExampleResponse,
# 	status_code=status.HTTP_200_OK,
# 	summary="Retrieve a single resource",
# 	response_description="Resource data found",
# )
# async def get(id: UUID4) -> ExampleResponse:
# 	"""
# 	Retrieve a single resource by its unique ID.

# 	- **id**: UUID of the resource
# 	- **Returns**: The resource data if found,
# 	otherwise triggers ObjectNotFound exception
# 	"""


# @router.get(
# 	"/",
# 	response_model=CollectionResponse[ExampleResponse],
# 	status_code=status.HTTP_200_OK,
# 	summary="Retrieve a list of resources",
# 	response_description="A paginated collection of resources",
# )
# async def query(
# 	request: Request,
# 	query_params: ExampleQueryParams = Depends(),
# ) -> CollectionResponse[ExampleResponse]:
# 	"""
# 	Retrieve a collection of resources filtered by optional query parameters.

# 	- **query_params**: Optional filters for the search
# 	- **Returns**: A paginated collection of resources matching the filters
# 	"""


@router.post(
	"/",
	# response_model=ExampleResponse,
	status_code=status.HTTP_201_CREATED,
	summary="Create a new resource",
	response_description="The newly created resource",
)
async def create(data: CreateSchema[ExampleCreate], producer: KafkaProducerDependency):
	await producer.send(event=data.model_dump(), topic=ExampleTopics.EXAMPLE_CREATED)

	"""RESOLVER QUESTÃO DOS TOPICOS criar ou não etc etc"""


# @router.post(
# 	"/bulk_insert",
# 	response_model=BulkInsertResponse,
# 	status_code=status.HTTP_200_OK,
# 	summary="Insert multiple resources in bulk",
# 	response_description="The newly created resource",
# )
# async def bulk_insert(
#     data: BulkInsertCreate[ExampleCreate], producer: KafkaProducerDependency
# ) -> BulkInsertResponse:
# 	"""
# 	Insert multiple resources in bulk with the provided data.

# 	- **data**: List of resource data to be inserted
# 	- **Returns**: The list of newly created resources
# 	"""
# 	await producer.send(
# 	    event=data.model_dump(),
# 		topic=ExampleTopics.EXAMPLE_BULK_INSERTED
# 	)

# @router.patch(
# 	"/{id}",
# 	response_model=ExampleResponse,
# 	status_code=status.HTTP_201_CREATED,
# 	summary="Partially update a resource",
# 	response_description="The updated resource",
# )
# async def partial_update(
#     data: ExampleUpdate,
#     id: UUID4,
#     producer: KafkaProducerDependency
# ) -> ExampleResponse:
# 	"""
# 	Partially update fields of an existing resource by ID.

# 	- **id**: UUID of the resource to update
# 	- **data**: Fields to update
# 	- **Returns**: The updated resource
# 	"""
# 	await producer.send(
# 	    event=data.model_dump(),
# 		topic=ExampleTopics.EXAMPLE_UPDATED
# 	)

# @router.delete(
# 	"/{id}",
# 	status_code=status.HTTP_204_NO_CONTENT,
# 	summary="Delete a resource",
# 	response_description="No content on successful deletion",
# )
# async def delete(id: UUID4, producer: KafkaProducerDependency) -> None:
# 	"""
# 	Delete a resource by its unique ID.

# 	- **id**: UUID of the resource to delete
# 	- **Returns**: No content (204) on successful deletion
# 	"""
# 	await producer.send(
# 	    event=...,
# 		topic=ExampleTopics.EXAMPLE_DELETED
# 	)
