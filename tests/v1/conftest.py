from httpx import AsyncClient
import pytest

from src.main import app
from src.v1.model import Part
from src.v1.repository import PartsRepository


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


@pytest.fixture
def part_payload():
    return {
        'name': 'Stepper motor',
        'quantity': 100,
        'description': 'NEMA 17 stepper motor',
    }


@pytest.fixture
def updated_part_payload():
    return {
        'name': 'DC motor',
        'quantity': 50,
        'description': '12V DC motor',
    }


@pytest.fixture
def parts_to_register():
    return [
        {
            'name': 'Stepper motor',
            'quantity': 100,
            'description': 'NEMA 17 stepper motor',
        },
        {
            'name': 'Encoder disc for Speed Sensor',
            'quantity': 50,
            'description': '12mm encoder disc',
        },
        {
            'name': 'Encoder HC 020K Double Speed Sensor',
            'quantity': 999,
            'description': 'HC 020K encoder',
        },
    ]
