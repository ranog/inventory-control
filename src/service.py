from src.repository import PartsRepository
from src.model import Part


async def register_part(part: Part, repository: PartsRepository = PartsRepository()) -> int:
    return {'part_number': await repository.create(part)}


async def part_details(part_number: int, repository: PartsRepository = PartsRepository()) -> Part:
    part = await repository.get(part_number)
    if part:
        return Part(name=part[1], quantity=part[2], description=part[3])


async def list_parts(repository: PartsRepository = PartsRepository()) -> list:
    parts = await repository.list()
    return [{'name': part[1], 'quantity': part[2], 'description': part[3]} for part in parts]
