import pytest

from src.v2.allocation.adapters import repository
from src.v2.allocation.domain import model
from src.v2.allocation.domain.model import Batch
from src.v2.allocation.service_layer import services


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


def test_returns_allocation():
    line = model.OrderLine(order_id='o1', sku='RED-CHAIR', qty=3)
    batch = model.Batch(ref='b1', sku='RED-CHAIR', qty=20, eta=None)
    repo = FakeRepository([batch])

    result = services.allocate(line=line, repo=repo, session=FakeSession())

    assert result == 'b1'


def test_error_for_invalid_sku():
    line = model.OrderLine(order_id='o1', sku='NON-EXISTENT', qty=3)
    batch = model.Batch(ref='b1', sku='AREALSKU', qty=20, eta=None)
    repo = FakeRepository([batch])

    with pytest.raises(services.InvalidSku, match='Invalid sku NON-EXISTENT'):
        services.allocate(line=line, repo=repo, session=FakeSession())


def test_commits():
    line = model.OrderLine(order_id='o1', sku='OMINOUS-MIRROR', qty=3)
    batch = model.Batch(ref='b1', sku='OMINOUS-MIRROR', qty=20, eta=None)
    repo = FakeRepository([batch])
    session = FakeSession()

    services.allocate(line=line, repo=repo, session=session)

    assert session.committed is True
