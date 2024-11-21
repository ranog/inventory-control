from typing import Protocol, Set

from src.v2.allocation.domain import model


class AbstractRepository(Protocol):
    def add(self, product: model.Product):
        ...

    def get(self, sku: str) -> model.Product:
        ...


class TrackingRepository:
    seen: Set[model.Product]

    def __init__(self, repo: AbstractRepository):
        self.seen = set()
        self._repo = repo

    def add(self, product: model.Product):
        self.seen.add(product)
        self._repo.add(product)

    def get(self, sku: str) -> model.Product:
        product = self._repo.get(sku)
        if product:
            self.seen.add(product)
        return product


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product: model.Product):
        self.session.add(product)

    def get(self, sku: str) -> model.Product:
        return self.session.query(model.Product).filter_by(sku=sku).first()
