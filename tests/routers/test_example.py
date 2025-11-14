from uuid import UUID

import pytest

from app.domain.schemas.bulk_insert import BulkInsertCreate
from app.domain.schemas.example import ExampleCreate, ExampleQueryParams, ExampleUpdate


@pytest.mark.asyncio
async def test_get_example_returns_200(
	async_client, mock_example_usecase, single_examaple_response_fac
):
	fake_data = single_examaple_response_fac()

	mock_example_usecase.get.return_value = fake_data
	response = await async_client.get(f"/example/{fake_data['id']}")

	assert response.status_code == 201
	assert response.json() == fake_data
	mock_example_usecase.get.assert_called_once_with(id=UUID(fake_data["id"]))


@pytest.mark.asyncio
async def test_query_example_returns_paginated_results(
	async_client, mock_example_usecase, mocker
):
	query_response = {
		"count": 2,
		"next": "http://0.0.0.0:8001/example/?limit=10&offset=10",
		"previous": "http://0.0.0.0:8001/example/?limit=10&offset=0",
		"results": [
			{
				"id": "3a4a0db4-e08e-496b-a548-9b59c85c1a42",
				"created_at": "2025-11-06T02:13:28.907473Z",
				"updated_at": "2025-11-06T02:13:28.907473Z",
				"name": "felipe",
				"age": 19,
			},
			{
				"id": "c354390c-87e4-4bc1-ab44-fa8232ce92d1",
				"created_at": "2025-11-06T02:13:28.907473Z",
				"updated_at": "2025-11-06T02:13:28.907473Z",
				"name": "gustavo",
				"age": 20,
			},
		],
	}
	mock_example_usecase.query.return_value = query_response
	response = await async_client.get("/example/?offset=0&limit=10")

	assert response.status_code == 200
	assert response.json() == query_response
	mock_example_usecase.query.assert_called_once_with(
		request=mocker.ANY,
		query_params=ExampleQueryParams(name=None, age=None, offset=0, limit=10),
	)


@pytest.mark.asyncio
async def test_create_example_returns_201_with_valid_data(
	async_client, mock_example_usecase, single_examaple_response_fac
):
	fake_data = single_examaple_response_fac()
	mock_example_usecase.create.return_value = fake_data
	response = await async_client.post("/example/", json={"name": "example", "age": 12})

	assert response.status_code == 201
	assert response.json() == fake_data
	mock_example_usecase.create.assert_called_once_with(
		data=ExampleCreate(name="example", age=12)
	)


@pytest.mark.asyncio
async def test_partial_update_example_updates_fields(
	async_client, mock_example_usecase, single_examaple_response_fac
):
	fake_data = single_examaple_response_fac()
	mock_example_usecase.partial_update.return_value = fake_data
	response = await async_client.patch(
		f"/example/{fake_data['id']}", json={"name": "example", "age": 12}
	)

	assert response.status_code == 201
	assert response.json() == fake_data
	mock_example_usecase.partial_update.assert_called_once_with(
		data=ExampleUpdate(name="example", age=12), id=UUID(fake_data["id"])
	)


@pytest.mark.asyncio
async def test_bulk_insert_example_inserts_multiple_records(
	async_client, mock_example_usecase
):
	json_data = {"items": [{"age": 19, "name": "felipe"}, {"age": 20, "name": "gustavo"}]}
	bulk_insert_response = {"elapsed_time": 1.0}
	mock_example_usecase.bulk_insert.return_value = bulk_insert_response
	response = await async_client.post("/example/bulk_insert", json=json_data)

	assert response.status_code == 200
	assert response.json() == bulk_insert_response
	mock_example_usecase.bulk_insert.assert_called_once_with(
		data=BulkInsertCreate[ExampleCreate](
			items=[
				ExampleCreate(name="felipe", age=19),
				ExampleCreate(name="gustavo", age=20),
			]
		)
	)


@pytest.mark.asyncio
async def test_delete_example_returns_204(
	async_client, mock_example_usecase, single_examaple_response_fac
):
	example_id = single_examaple_response_fac()["id"]
	mock_example_usecase.delete.return_value = None
	response = await async_client.delete(f"/example/{example_id}")

	assert response.status_code == 204
	assert response.text == ""
	mock_example_usecase.delete.assert_called_once_with(id=UUID(example_id))
