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


async def test_it_should_update_part_data_in_the_database(part: Part, updated_part_payload: dict):
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)

    await part_repository.update(part_number=part_number, data_to_update=updated_part_payload)

    assert await part_repository.get(part_number) != part


async def test_it_should_only_update_the_name_of_the_part(part):
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)
    data_to_update = {'name': 'DC motor'}

    await part_repository.update(part_number=part_number, data_to_update=data_to_update)

    updated_part = await part_repository.get(part_number)
    _, name, quantity, description, created_at, updated_at = updated_part

    assert name == data_to_update['name']
    assert quantity == part.quantity
    assert description == part.description
    assert created_at == part.created_at
    assert updated_at != part.updated_at


async def test_it_should_only_update_the_quantity_of_the_part(part):
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)
    data_to_update = {'quantity': 50}

    await part_repository.update(part_number=part_number, data_to_update=data_to_update)

    updated_part = await part_repository.get(part_number)
    _, name, quantity, description, created_at, updated_at = updated_part

    assert quantity == data_to_update['quantity']
    assert name == part.name
    assert description == part.description
    assert created_at == part.created_at
    assert updated_at != part.updated_at


async def test_it_should_only_update_the_description_of_the_part(part):
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)
    data_to_update = {'description': '12V DC motor'}

    await part_repository.update(part_number=part_number, data_to_update=data_to_update)

    updated_part = await part_repository.get(part_number)
    _, name, quantity, description, created_at, updated_at = updated_part

    assert description == data_to_update['description']
    assert name == part.name
    assert quantity == part.quantity
    assert created_at == part.created_at
    assert updated_at != part.updated_at


async def test_it_should_delete_the_record_from_the_database(part: Part):
    part_repository = PartsRepository()
    part_number = await part_repository.create(part)

    await part_repository.delete(part_number)

    assert await part_repository.get(part_number) is None
