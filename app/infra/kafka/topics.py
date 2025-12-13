from enum import StrEnum


class ExampleTopics(StrEnum):
	EXAMPLE_CREATED = "example.created"
	EXAMPLE_BULK_INSERTED = "example.bulk_inserted"
	EXAMPLE_UPDATED = "example.updated"
	EXAMPLE_DELETED = "example.deleted"
	# EXAMPLE_BULK_INSERT = "example.bulk_inserted"

	# # QUERY events (opcional, depende da estratégia)
	# EXAMPLE_ACCESSED = "example.accessed"   # GET /{id}
	# EXAMPLE_LIST_QUERIED = "example.list_queried"  # GET /
