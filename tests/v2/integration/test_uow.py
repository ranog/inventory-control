import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.v2.allocation.domain import model
from src.v2.allocation.service_layer import unit_of_work


def insert_batch(session, ref, sku, qty, eta, product_version=1):
    session.execute(
        text('INSERT INTO products (sku, version_number) VALUES (:sku, :version)'),
        dict(sku=sku, version=product_version),
    )
    session.execute(
        text('INSERT INTO batches (reference, sku, _purchased_quantity, eta)' ' VALUES (:ref, :sku, :qty, :eta)'),
        dict(ref=ref, sku=sku, qty=qty, eta=eta),
    )


def get_allocated_batch_ref(session: Session, order_id: str, sku: str):
    [[orderlineid]] = session.execute(
        text('SELECT id FROM order_lines WHERE order_id=:order_id AND sku=:sku'),
        dict(order_id=order_id, sku=sku),
    )
    [[batchref]] = session.execute(
        text(
            'SELECT b.reference FROM allocations JOIN batches AS b ON batch_id = b.id'
            ' WHERE orderline_id=:orderlineid'
        ),
        dict(orderlineid=orderlineid),
    )
    return batchref


def test_uow_can_retrieve_a_batch_and_allocate_to_it(session_factory):
    session = session_factory()
    insert_batch(session=session, ref='batch1', sku='HIPSTER-WORKBENCH', qty=100, eta=None)
    session.commit()
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)

    with uow:
        product = uow.products.get(sku='HIPSTER-WORKBENCH')
        line = model.OrderLine(order_id='o1', sku='HIPSTER-WORKBENCH', qty=10)
        product.allocate(line)
        uow.commit()

    batch_ref = get_allocated_batch_ref(session=session, order_id='o1', sku='HIPSTER-WORKBENCH')
    assert batch_ref == 'batch1'


def test_rolls_back_uncommitted_work_by_default(session_factory):
    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)

    with uow:
        insert_batch(session=uow.session, ref='batch1', sku='MEDIUM-PLINTH', qty=100, eta=None)

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    uow = unit_of_work.SqlAlchemyUnitOfWork(session_factory)

    with pytest.raises(MyException):
        with uow:
            insert_batch(session=uow.session, ref='batch1', sku='LARGE-SPOON', qty=100, eta=None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []
