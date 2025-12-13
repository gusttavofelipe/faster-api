import json

from aiokafka import AIOKafkaConsumer

from app.core.config import settings


class KafkaConsumerService:
	def __init__(self) -> None:
		self._consumer: AIOKafkaConsumer | None = None

	async def start(self, topic: str, handler) -> None:
		self._consumer = AIOKafkaConsumer(
			topic,
			bootstrap_servers=settings.KAFKA_BOOTSTRAP_SERVERS,
			group_id=settings.KAFKA_GROUP_ID,
			client_id=settings.KAFKA_CLIENT_ID,
			value_deserializer=lambda v: json.loads(v.decode("utf-8")),
			enable_auto_commit=True,
			auto_offset_reset="latest",
		)

		await self._consumer.start()

		try:
			async for msg in self._consumer:
				await handler(msg.value)
		finally:
			await self._consumer.stop()

	async def shutdown(self) -> None:
		if self._consumer:
			await self._consumer.stop()
			self._consumer = None
