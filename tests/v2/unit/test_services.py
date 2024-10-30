import pytest
from datetime import date, timedelta

from src.v2.allocation.adapters import repository
from src.v2.allocation.domain.model import Batch, Product
from src.v2.allocation.service_layer import services, unit_of_work

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def commit(self):
        self.committed = True

    def rollback(self):
        pass


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products: list):
        self._products = set(products)

    def add(self, product: Product):
        self._products.add(product)

    def get(self, sku: str) -> Batch:
        return next((p for p in self._products if p.sku == sku), None)


def test_add_batch_for_new_product():
    uow = FakeUnitOfWork()

    services.add_batch(ref='b1', sku='CRUNCHY-ARMCHAIR', qty=100, eta=None, uow=uow)

    assert uow.products.get('CRUNCHY-ARMCHAIR') is not None
    assert uow.committed


def test_add_batch_for_existing_product():
    uow = FakeUnitOfWork()

    services.add_batch('b1', 'GARISH-RUG', 100, None, uow)
    services.add_batch('b2', 'GARISH-RUG', 99, None, uow)

    assert 'b2' in [b.reference for b in uow.products.get('GARISH-RUG').batches]


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
