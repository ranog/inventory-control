from httpx import AsyncClient
import pytest
from src.main import app


@pytest.fixture
async def async_http_client():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        yield async_client


async def test_it_should_ping_successfully(async_http_client: AsyncClient):
    response = await async_http_client.get('/v1/ping/')

    assert response.status_code == 200
    assert response.json() == {'ping': 'pong'}
