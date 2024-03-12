import pytest

from src.repository import PartsRepository


@pytest.fixture(autouse=True)
def clear_repository():
    parts_repository = PartsRepository()
    parts_repository.collection.execute('DELETE FROM parts')
    parts_repository.collection.commit()
    parts_repository.collection.close()
