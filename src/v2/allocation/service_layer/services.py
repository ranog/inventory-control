from datetime import date
from typing import Optional

from src.v2.allocation.domain import model
from src.v2.allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def is_valid_sku(sku: str, batches: list[model.Batch]) -> bool:
    return sku in {batch.sku for batch in batches}


def allocate(order_id: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> str:
    with uow:
        batches = uow.batches.list()
        if not is_valid_sku(sku=sku, batches=batches):
            raise InvalidSku(f'Invalid sku {sku}')
        batch_ref = model.allocate(line=model.OrderLine(order_id=order_id, sku=sku, qty=qty), batches=batches)
        uow.commit()
    return batch_ref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        uow.batches.add(model.Batch(ref=ref, sku=sku, qty=qty, eta=eta))
        uow.commit()
