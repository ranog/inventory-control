import random
from src.model import Part
from src.service import (
    delete_part_record,
    list_parts,
    part_details,
    register_part,
    update_part,
)


async def test_it_should_register_a_part_in_the_database(part):
    part_number = await register_part(part)

    expected_result = await part_details(part_number['part_number'])

    assert part == expected_result


async def test_it_should_return_all_parts_registered_in_the_database(parts_to_register: list[dict]):
    for part_data in parts_to_register:
        await register_part(Part(**part_data))

    database_parts = await list_parts()

    assert len(parts_to_register) == len(database_parts)


async def test_it_should_return_empty_list_when_no_parts_registered_in_the_database():
    database_parts = await list_parts()

    assert database_parts == []


async def test_created_at_field_should_not_be_empty_when_the_part_is_registered(part):
    part_number = await register_part(part)

    created_part = await part_details(part_number['part_number'])

    assert created_part.created_at is not None


async def test_updated_at_field_should_not_be_empty_when_the_part_is_updated(part):
    part_number = await register_part(part)
    updated_part = Part(name='DC motor', quantity=50, description='12V DC motor')

    await update_part(part_number=part_number['part_number'], data_to_update=updated_part)

    part = await part_details(part_number['part_number'])
    assert part.updated_at is not None


async def test_it_should_return_the_part_details_from_the_database(part):
    part_number = await register_part(part)

    expected_result = await part_details(part_number['part_number'])

    assert part == expected_result


async def test_it_should_update_part_data_in_the_database(part, updated_part_payload: dict):
    part_number = await register_part(part)

    await update_part(part_number=part_number['part_number'], data_to_update=updated_part_payload)

    expected_result = await part_details(part_number['part_number'])

    assert updated_part_payload['name'] == expected_result.name
    assert updated_part_payload['quantity'] == expected_result.quantity
    assert updated_part_payload['description'] == expected_result.description


async def test_it_should_update_part_with_partial_data(part):
    part_number = await register_part(part)
    updated_part_payload = {'name': 'DC motor'}

    await update_part(part_number=part_number['part_number'], data_to_update=updated_part_payload)

    expected_result = await part_details(part_number['part_number'])

    assert updated_part_payload['name'] == expected_result.name
    assert part.quantity == expected_result.quantity
    assert part.description == expected_result.description


async def test_it_should_delete_the_record_from_the_database(part):
    part_number = await register_part(part)

    await delete_part_record(part_number['part_number'])

    assert await part_details(part_number['part_number']) is None


async def test_it_should_return_none_when_the_part_number_does_not_exist_in_the_database():
    part_number = 1000

    part = await part_details(part_number)

    assert part is None


async def test_it_should_return_none_when_the_part_number_is_deleted_from_the_database(part):
    part_number = await register_part(part)

    await delete_part_record(part_number['part_number'])

    part = await part_details(part_number['part_number'])

    assert part is None


async def test_it_should_only_delete_the_part_number_passed(parts_to_register):
    part_numbers = [await register_part(Part(**part_data)) for part_data in parts_to_register]

    await delete_part_record(part_numbers[random.randint(0, len(part_numbers) - 1)]['part_number'])

    assert len(parts_to_register) - 1 == len(await list_parts())
