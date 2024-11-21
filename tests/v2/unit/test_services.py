import pytest

from src.v2.allocation.adapters import repository
from src.v2.allocation.service_layer import unit_of_work, services


class FakeRepository(repository.AbstractRepository):
    def __init__(self, products):
        self._products = set(products)
        self.seen = set()

    def add(self, product):
        self._products.add(product)
        self.seen.add(product)

    def get(self, sku):
        product = next((p for p in self._products if p.sku == sku), None)
        if product:
            self.seen.add(product)
        return product


class FakeUnitOfWork(unit_of_work.AbstractUnitOfWork):
    def __init__(self):
        self.products = FakeRepository([])
        self.committed = False

    def _commit(self):
        self.committed = True

    def rollback(self):
        pass


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
