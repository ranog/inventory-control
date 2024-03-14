from src.model import Part
from src.service import (
    list_parts,
    part_details,
    register_part,
    update_part,
)


async def test_it_should_register_a_part_in_the_database(part):
    part_number = await register_part(part)

    expected_result = await part_details(part_number['part_number'])

    assert part == expected_result


async def test_it_should_return_all_parts_registered_in_the_database():
    parts_to_register = [
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
