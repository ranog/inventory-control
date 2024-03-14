from src.repository import PartsRepository
from src.model import Part


async def register_part(part: Part, repository: PartsRepository = PartsRepository()) -> int:
    return {'part_number': await repository.create(part)}


async def part_details(part_number: int, repository: PartsRepository = PartsRepository()) -> Part:
    part = await repository.get(part_number)
    if part:
        part_attributes = (
            'id',
            'name',
            'quantity',
            'description',
            'created_at',
            'updated_at',
        )
        part_data = dict(zip(part_attributes, part))
        return Part(**part_data)


async def list_parts(repository: PartsRepository = PartsRepository()) -> list:
    parts = await repository.list()

    parts_data = []
    for part in parts:
        part_attributes = (
            'id',
            'name',
            'quantity',
            'description',
            'created_at',
            'updated_at',
        )
        parts_data.append(dict(zip(part_attributes, part)))

    return parts_data


async def update_part(
    part_number: int,
    data_to_update: dict,
    repository: PartsRepository = PartsRepository(),
) -> None:
    await repository.update(part_number=part_number, data_to_update=data_to_update)


async def delete_part_record(part_number: int, repository: PartsRepository = PartsRepository()) -> None:
    await repository.delete(part_number)
