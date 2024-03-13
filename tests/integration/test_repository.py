from src.repository import PartsRepository
from src.model import Part


async def test_it_should_persist_in_the_repository():
    part = Part(name='Stepper motor', quantity=100, description='NEMA 17 stepper motor')
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)

    created_part = await part_repository.get(part_number)

    assert created_part == (part_number, part.name, part.quantity, part.description)
