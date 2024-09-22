import pytest
from datetime import date, timedelta

from src.v2.allocation.adapters import repository
from src.v2.allocation.domain.model import Batch
from src.v2.allocation.service_layer import services

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


class FakeRepository(repository.AbstractRepository):
    def __init__(self, batches: list):
        self._batches = set(batches)

    def add(self, batch: Batch):
        self._batches.add(batch)

    def get(self, reference: str) -> Batch:
        return next(b for b in self._batches if b.reference == reference)

    def list(self) -> list:
        return list(self._batches)


class FakeSession:
    committed = False

    def commit(self):
        self.committed = True


def test_add_batch():
    repo, session = FakeRepository([]), FakeSession()

    services.add_batch(ref='b1', sku='CRUNCHY-ARMCHAIR', qty=100, eta=None, repo=repo, session=session)

    assert repo.get('b1') is not None
    assert session.committed


def test_returns_allocation():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(ref='batch1', sku='RED-CHAIR', qty=20, eta=None, repo=repo, session=session)

    result = services.allocate(order_id='o1', sku='RED-CHAIR', qty=3, repo=repo, session=session)

    assert result == 'batch1'


def test_error_for_invalid_sku():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(ref='batch1', sku='MAGICAL-CHALICE', qty=20, eta=None, repo=repo, session=session)

    with pytest.raises(services.InvalidSku, match='Invalid sku NON-EXISTENT'):
        services.allocate(order_id='o1', sku='NON-EXISTENT', qty=3, repo=repo, session=session)


def test_commits():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(ref='b1', sku='OMINOUS-MIRROR', qty=20, eta=None, repo=repo, session=session)

    services.allocate(order_id='o1', sku='OMINOUS-MIRROR', qty=3, repo=repo, session=session)

    assert session.committed is True


def test_prefers_warehouse_batches_to_shipments():
    repo, session = FakeRepository([]), FakeSession()
    services.add_batch(ref='in-stock-batch', sku='RETRO-CLOCK', qty=100, eta=None, repo=repo, session=session)
    services.add_batch(ref='shipment-batch', sku='RETRO-CLOCK', qty=100, eta=tomorrow, repo=repo, session=session)

    services.allocate(order_id='order-123', sku='RETRO-CLOCK', qty=10, repo=repo, session=session)

    assert repo.get('in-stock-batch').available_quantity == 90
    assert repo.get('shipment-batch').available_quantity == 100
