from httpx import AsyncClient
import pytest
from src.service import part_details
from src.main import app


@pytest.fixture
async def async_http_client():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        yield async_client


async def test_it_should_ping_successfully(async_http_client: AsyncClient):
    response = await async_http_client.get('/v1/ping/')

    assert response.status_code == 200
    assert response.json() == 'pong'


async def test_it_should_register_part(async_http_client: AsyncClient):
    part_payload = {
        'name': 'Stepper motor',
        'quantity': 100,
        'description': 'NEMA 17 stepper motor',
    }

    response = await async_http_client.post('/v1/parts/', json=part_payload)

    expected_result = await part_details(response.json()['part_number'])

    assert response.status_code == 200
    assert part_payload['name'] == expected_result.name
    assert part_payload['quantity'] == expected_result.quantity
    assert part_payload['description'] == expected_result.description


async def test_it_should_return_400_when_registering_part_with_invalid_payload(
    async_http_client: AsyncClient,
):
    part_payload = {
        'name': 'Stepper motor',
        'quantity': 100,
    }
    expected_error = [
        {
            'loc': ['body', 'description'],
            'msg': 'field required',
            'type': 'value_error.missing',
        }
    ]

    response = await async_http_client.post('/v1/parts/', json=part_payload)

    assert response.status_code == 400
    assert response.json()['errors'] == expected_error
