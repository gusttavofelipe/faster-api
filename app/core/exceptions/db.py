from app.core.exceptions.base import CustomBaseException


class DatabaseConnectionError(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message = (
			message or "An error occurred while trying to connect to the database"
		)
		super().__init__(*args, self.message)


class DBOperationError(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message = message or "A database operation error has occurred"
		super().__init__(*args, self.message)


class ObjectNotFound(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message = message or "Object Not Found"
		super().__init__(*args, self.message)


class ObjectAlreadyExistError(CustomBaseException):
	def __init__(self, *args: object, message: str | None = None) -> None:
		self.message = message or "Objtect already exists"
		super().__init__(*args, self.message)
