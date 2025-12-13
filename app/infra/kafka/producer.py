"""app/infra/kafka/producer.py"""

import json
from typing import Annotated, Any

from aiokafka import AIOKafkaProducer
from fastapi import Depends

from app.core.config import settings


class KafkaProducerService:
	def __init__(self) -> None:
		self._producer: AIOKafkaProducer | None = None

	async def start(self) -> None:
		if self._producer:
			return

		self._producer = AIOKafkaProducer(
			bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
			client_id=settings.KAFKA_CLIENT_ID,
			value_serializer=lambda v: json.dumps(v).encode("utf-8"),
		)
		await self._producer.start()

	async def send(self, event: dict[str, Any], topic: str | None = None) -> None:
		if not self._producer:
			raise RuntimeError("KafkaProducer not initialized. Call connect().")

		await self._producer.send_and_wait(topic, event)

	async def shutdown(self) -> None:
		if self._producer:
			await self._producer.stop()
			self._producer = None


kafka_producer: KafkaProducerService = KafkaProducerService()


async def get_kafka_producer() -> KafkaProducerService:
	return kafka_producer


KafkaProducerDependency = Annotated[KafkaProducerService, Depends(get_kafka_producer)]
