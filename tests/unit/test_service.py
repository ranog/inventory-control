from src.service import list_parts, part_details, register_part
from src.model import Part


async def test_it_should_register_a_part_in_the_database():
    part = Part(name='Stepper motor', quantity=100, description='NEMA 17 stepper motor')
    part_number = await register_part(part)

    expected_result = await part_details(part_number['part_number'])

    assert part == expected_result


async def test_it_should_return_all_parts_registered_in_the_database():
    part_1 = Part(name='Stepper motor', quantity=100, description='NEMA 17 stepper motor')
    part_2 = Part(name='Encoder disc for Speed Sensor', quantity=50, description='12mm encoder disc')
    part_3 = Part(name='Encoder HC 020K Double Speed Sensor', quantity=999, description='HC 020K encoder')
    await register_part(part_1)
    await register_part(part_2)
    await register_part(part_3)

    expected_result = [
        {'name': 'Stepper motor', 'quantity': 100, 'description': 'NEMA 17 stepper motor'},
        {'name': 'Encoder disc for Speed Sensor', 'quantity': 50, 'description': '12mm encoder disc'},
        {'name': 'Encoder HC 020K Double Speed Sensor', 'quantity': 999, 'description': 'HC 020K encoder'},
    ]

    assert expected_result == await list_parts()
