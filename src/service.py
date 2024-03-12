from src.repository import PartsRepository
from src.model import Part


async def register_part(part: Part, repository: PartsRepository = PartsRepository()) -> int:
    return await repository.create(part)


async def part_details(part_number: int, repository: PartsRepository = PartsRepository()) -> Part:
    return await repository.get(part_number)
