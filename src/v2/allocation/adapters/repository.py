import abc

from src.v2.allocation.domain import model


class AbstractRepository(abc.ABC):
    @abc.abstractmethod
    def add(self, product: model.Product):
        raise NotImplementedError

    @abc.abstractmethod
    def get(self, sku) -> model.Product:
        raise NotImplementedError


class SqlAlchemyRepository(AbstractRepository):
    def __init__(self, session):
        self.session = session

    def add(self, product: model.Product):
        self.session.add(product)

    def get(self, sku) -> model.Product:
        return self.session.query(model.Product).filter_by(sku=sku).first()
