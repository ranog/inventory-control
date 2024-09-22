from datetime import date
from typing import Optional

from src.v2.allocation.adapters import orm
from src.v2.allocation.adapters.repository import AbstractRepository
from src.v2.allocation.domain import model
from src.v2.allocation.domain.model import Batch, OrderLine


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[Batch]) -> bool:
    return sku in {batch.sku for batch in batches}


def allocate(order_id: str, sku: str, qty: int, repo: AbstractRepository, session) -> str:
    batches = repo.list()
    if not is_valid_sku(sku=sku, batches=batches):
        raise InvalidSku(f'Invalid sku {sku}')
    batch_ref = model.allocate(line=OrderLine(order_id=order_id, sku=sku, qty=qty), batches=batches)
    session.commit()
    return batch_ref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], repo: AbstractRepository, session) -> None:
    orm.create_tables()
    repo.add(model.Batch(ref=ref, sku=sku, qty=qty, eta=eta))
    session.commit()
