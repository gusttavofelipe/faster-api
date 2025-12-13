from typing import Any

from app.api.example.schemas import BulkInsertCreate, ExampleCreate, ExampleUpdate
from app.core.logging import logger


class ExampleEventHandler:
	"""
	Handlers de eventos do domínio Example
	"""

	def __init__(self, usecase):
		self.usecase = usecase

	async def handle_create(self, event: dict[str, Any]) -> None:
		try:
			logger.info(f"[CREATE] Evento recebido: {event}")
			data = ExampleCreate.model_validate(event)
			await self.usecase.create(data=data)
			logger.info("[CREATE] Evento processado com sucesso")
		except Exception as e:
			logger.exception(f"[CREATE] Erro ao processar evento: {e}")

	async def handle_partial_update(self, event: dict[str, Any]) -> None:
		try:
			logger.info(f"[UPDATE] Evento recebido: {event}")
			id = event.get("id")
			data = ExampleUpdate.model_validate(event)
			await self.usecase.partial_update(data=data, id=id)
			logger.info("[UPDATE] Evento processado com sucesso")
		except Exception as e:
			logger.exception(f"[UPDATE] Erro ao processar evento: {e}")

	async def handle_delete(self, event: dict[str, Any]) -> None:
		try:
			logger.info(f"[DELETE] Evento recebido: {event}")
			id = event.get("id")
			await self.usecase.delete(id=id)
			logger.info("[DELETE] Evento processado com sucesso")
		except Exception as e:
			logger.exception(f"[DELETE] Erro ao processar evento: {e}")

	async def handle_bulk_insert(self, event: dict[str, Any]) -> None:
		try:
			logger.info("[BULK_INSERT] Evento recebido")
			data = BulkInsertCreate.model_validate(event)
			await self.usecase.bulk_insert(data=data)
			logger.info("[BULK_INSERT] Evento processado com sucesso")
		except Exception as e:
			logger.exception(f"[BULK_INSERT] Erro ao processar evento: {e}")
