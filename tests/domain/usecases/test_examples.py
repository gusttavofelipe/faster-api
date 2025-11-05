from uuid import UUID

import pytest


@pytest.mark.asyncio
async def test_get_example_success(async_client, mock_example_usecase, fake_response):
	fake_data = fake_response()

	# define o retorno correto do método async
	mock_example_usecase.get.return_value = fake_data

	response = await async_client.get(f"/example/{fake_data['id']}")

	assert response.status_code == 200
	assert response.json() == fake_data
	mock_example_usecase.get.assert_called_once_with(id=UUID(fake_data["id"]))
