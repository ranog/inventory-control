from datetime import date
from typing import Optional

from src.v2.allocation.domain import model
from src.v2.allocation.service_layer import unit_of_work


class InvalidSku(Exception):
    pass


def allocate(order_id: str, sku: str, qty: int, uow: unit_of_work.AbstractUnitOfWork) -> str:
    line = model.OrderLine(order_id=order_id, sku=sku, qty=qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f'Invalid sku {line.sku}')
        batch_ref = product.allocate(line=line)
        uow.commit()
        return batch_ref


def add_batch(ref: str, sku: str, qty: int, eta: Optional[date], uow: unit_of_work.AbstractUnitOfWork) -> None:
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product = model.Product(sku=sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref=ref, sku=sku, qty=qty, eta=eta))
        uow.commit()
