from app.core.logging import logger
from app.core.config import settings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Any, AsyncGenerator
from app.core.exceptions.db import DatabaseConnectionError
from app.core.logging import LOGGING_CONFIG
from app.routers.example import router as example_router
from app.core.exceptions.handlers import register_exception_handlers
from app.infra.db.manager import DatabaseManager
import uvicorn


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown."""
    try:
        await DatabaseManager.test_connection()
    except Exception as exc:
        raise DatabaseConnectionError(
            message=f"Unable to connect to the database: {exc}"
        )
    logger.info("Database healthy")

    yield


class App(FastAPI):
    """Custom FastAPI application class"""

    def __init__(self, *args: tuple[Any, ...], **kwargs: Any) -> None:
        """Initializes the FastAPI application
        with default settings and lifespan.
        """
        super().__init__(
            *args,
            **kwargs,
            title=settings.APP_TITLE,
            version=settings.APP_VERSION,
            description=settings.APP_DESCRIPTION,
            lifespan=lifespan,
        )
        self.__include_routers()
        self.__register_exception_handlers()

    def __register_exception_handlers(self) -> None:
        """Registers all exception handlers for the application"""
        register_exception_handlers(self)

    def __include_routers(self) -> None:
        """Includes all predefined API routers into the application"""
        self.include_router(example_router)


app: FastAPI = App()


if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8001,
        log_config=LOGGING_CONFIG,
        reload=True,
    )
