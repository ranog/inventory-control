from src.service import part_details, register_part
from src.model import Part


async def test_it_should_register_a_part_in_the_database():
    part = Part(name='Stepper motor', quantity=100, description='NEMA 17 stepper motor')
    part_number = await register_part(part)

    expected_result = await part_details(part_number['part_number'])

    assert part == expected_result
