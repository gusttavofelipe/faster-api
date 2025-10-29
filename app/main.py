from app.core.config import settings
from contextlib import asynccontextmanager
from fastapi import FastAPI
from typing import Any, AsyncGenerator
from app.core.exceptions.db import DatabaseConnectionError
from app.core.logging import LOGGING_CONFIG
from app.routers.example import router as example_router
import uvicorn


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncGenerator[None, None]:
    """Manages application startup and shutdown.

        Args:
            _ (FastAPI): FastAPI app instance (unused in function).

        Raises:
            RuntimeError:
                Error when the database is not healthy, prevents the app from starting

        Yields:
            None: This context manager does not yield any value.
    """

    healthy = True # await test_connection()
    if not healthy:
        raise DatabaseConnectionError(message="Unable to connect to the database")
    yield


class App(FastAPI):
    """ Custom FastAPI application class"""

    def __init__(self, *args: tuple[Any, ...], **kwargs: Any) -> None:
        """Initializes the FastAPI application with default settings and lifespan.

        This constructor wraps the FastAPI initialization, providing default
        values for title, version, description, and lifespan. It also includes
        routers automatically after initialization.

        Args:
            args (tuple[Any, ...]): Positional arguments passed to the FastAPI constructor.
            kwargs (Any): Keyword arguments passed to the FastAPI constructor.
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
        reload=True
    )