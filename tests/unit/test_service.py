from src.model import Part
from src.service import list_parts, part_details, register_part


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

    assert parts_to_register == database_parts
