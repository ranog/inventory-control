from httpx import AsyncClient
import pytest

from src.main import app
from src.model import Part
from src.repository import PartsRepository


@pytest.fixture
async def async_http_client():
    async with AsyncClient(app=app, base_url='http://test') as async_client:
        yield async_client


@pytest.fixture(autouse=True)
def clear_repository():
    parts_repository = PartsRepository()
    parts_repository.collection.execute('DELETE FROM parts')
    parts_repository.collection.commit()
    parts_repository.collection.close()


@pytest.fixture
def part():
    return Part(name='Stepper motor', quantity=100, description='NEMA 17 stepper motor')
