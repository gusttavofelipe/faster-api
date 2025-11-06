from contextlib import contextmanager
from datetime import UTC, datetime
from uuid import uuid4

import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.domain.usecases.example import ExampleUsecase
from app.main import app


@pytest_asyncio.fixture
async def async_client():
	"""Shared async client for all route tests."""
	transport = ASGITransport(app=app)
	async with AsyncClient(transport=transport, base_url="http://test") as client:
		yield client


@pytest.fixture
def mock_usecase(mocker):
	"""Mock for ExampleUsecase using pytest-mock."""
	mock = mocker.MagicMock()
	mock.get = mocker.AsyncMock()
	mock.query = mocker.AsyncMock()
	mock.create = mocker.AsyncMock()
	mock.delete = mocker.AsyncMock()
	mock.bulk_insert = mocker.AsyncMock()
	mock.partial_update = mocker.AsyncMock()
	return mock


@contextmanager
def override_dependency(app, dependency, replacement):
	original = app.dependency_overrides.get(dependency)
	app.dependency_overrides[dependency] = lambda: replacement
	try:
		yield
	finally:
		if original is not None:
			app.dependency_overrides[dependency] = original
		else:
			app.dependency_overrides.pop(dependency, None)


@pytest.fixture
def mock_example_usecase(mock_usecase):
	"""Automatically override ExampleUsecase for all tests."""
	with override_dependency(
		app=app, dependency=ExampleUsecase, replacement=mock_usecase
	):
		yield mock_usecase


@pytest.fixture
def single_examaple_response_fac():
	def _factory(**overrides):
		now = datetime.now(UTC).isoformat().replace("+00:00", "Z")
		base = {
			"id": str(uuid4()),
			"created_at": now,
			"updated_at": now,
			"name": "example",
			"age": 12,
		}
		return {**base, **overrides}

	return _factory
