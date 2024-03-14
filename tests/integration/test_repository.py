from src.repository import PartsRepository


async def test_it_should_persist_in_the_repository(part):
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)

    created_part = await part_repository.get(part_number)

    assert created_part == (part_number, part.name, part.quantity, part.description, part.created_at)
