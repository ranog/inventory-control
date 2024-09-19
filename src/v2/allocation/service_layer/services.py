from src.v2.allocation.adapters.repository import AbstractRepository
from src.v2.allocation.domain import model
from src.v2.allocation.domain.model import Batch, OrderLine


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[Batch]) -> bool:
    return sku in {batch.sku for batch in batches}


def allocate(line: OrderLine, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(sku=line.sku, batches=batches):
        raise InvalidSku(f'Invalid sku {line.sku}')
    batch_ref = model.allocate(line=line, batches=batches)
    session.commit()
    return batch_ref
