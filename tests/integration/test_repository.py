from src.model import Part
from src.repository import PartsRepository


async def test_it_should_persist_in_the_repository(part):
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)

    created_part = await part_repository.get(part_number)

    assert created_part == (
        part_number,
        part.name,
        part.quantity,
        part.description,
        part.created_at,
        part.updated_at,
    )


async def test_it_should_update_part_data_in_the_database(part):
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)
    await part_repository.update(
        part_number=part_number,
        part=Part(name='DC motor', quantity=50, description='12V DC motor'),
    )

    updated_part = await part_repository.get(part_number)

    assert updated_part != part
