import pytest
from datetime import date, timedelta

from src.v2.allocation.adapters import repository
from src.v2.allocation.domain.model import Batch
from src.v2.allocation.service_layer import services, unit_of_work

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.batches = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches: list):
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def get(self, reference: str) -> Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list:
        return list(self._batches)


def test_add_batch():
    uow = FakeUnitOfWork()

    services.add_batch(ref='b1', sku='CRUNCHY-ARMCHAIR', qty=100, eta=None, uow=uow)

    assert uow.batches.get('b1') is not None
    assert uow.committed


def test_returns_allocation():
    uow = FakeUnitOfWork()
    services.add_batch(ref='batch1', sku='RED-CHAIR', qty=20, eta=None, uow=uow)

    result = services.allocate(order_id='o1', sku='RED-CHAIR', qty=3, uow=uow)

    assert result == 'batch1'


def test_error_for_invalid_sku():
    uow = FakeUnitOfWork()
    services.add_batch(ref='batch1', sku='MAGICAL-CHALICE', qty=20, eta=None, uow=uow)

    with pytest.raises(services.InvalidSku, match='Invalid sku NON-EXISTENT'):
        services.allocate(order_id='o1', sku='NON-EXISTENT', qty=3, uow=uow)


def test_commits():
    uow = FakeUnitOfWork()
    services.add_batch(ref='b1', sku='OMINOUS-MIRROR', qty=20, eta=None, uow=uow)

    services.allocate(order_id='o1', sku='OMINOUS-MIRROR', qty=3, uow=uow)

    assert uow.committed is True


def test_prefers_warehouse_batches_to_shipments():
    uow = FakeUnitOfWork()
    services.add_batch(ref='in-stock-batch', sku='RETRO-CLOCK', qty=100, eta=None, uow=uow)
    services.add_batch(ref='shipment-batch', sku='RETRO-CLOCK', qty=100, eta=tomorrow, uow=uow)

    services.allocate(order_id='order-123', sku='RETRO-CLOCK', qty=10, uow=uow)

    assert uow.batches.get('in-stock-batch').available_quantity == 90
    assert uow.batches.get('shipment-batch').available_quantity == 100
