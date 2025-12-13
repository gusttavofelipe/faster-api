import asyncio
from collections.abc import Callable
from typing import Any

from app.api.events.handlers.example import ExampleEventHandler
from app.infra.kafka.consumer import KafkaConsumerService
from app.infra.kafka.topics import ExampleTopics


class ExampleEventConsumer:
	"""
	Consumer de eventos do domínio Example para todos os endpoints
	"""

	def __init__(self, usecase):
		self.consumer = KafkaConsumerService()
		self.handlers = ExampleEventHandler(usecase)

		# Mapeia tópicos para handlers
		self.event_handlers: dict[str, Callable[[dict[str, Any]], Any]] = {
			ExampleTopics.EXAMPLE_CREATED: self.handlers.handle_create,
			ExampleTopics.EXAMPLE_UPDATED: self.handlers.handle_partial_update,
			ExampleTopics.EXAMPLE_DELETED: self.handlers.handle_delete,
			ExampleTopics.EXAMPLE_BULK_INSERTED: self.handlers.handle_bulk_insert,
		}

	async def start(self) -> None:
		tasks = [
			asyncio.create_task(self.consumer.start(topic=topic, handler=handler))
			for topic, handler in self.event_handlers.items()
		]
		await asyncio.gather(*tasks)

	async def shutdown(self) -> None:
		await self.consumer.shutdown()
