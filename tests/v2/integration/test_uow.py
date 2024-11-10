import threading
import time
import traceback

import pytest
from sqlalchemy import text
from sqlalchemy.orm import Session

from src.v2.allocation.domain import model
from src.v2.allocation.service_layer import unit_of_work
from tests.v2.conftest import random_batch_ref, random_sku, random_order_id


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

    with unit_of_work.SqlAlchemyUnitOfWork(session_factory) as uow:
        product = uow.products.get(sku='HIPSTER-WORKBENCH')
        line = model.OrderLine(order_id='o1', sku='HIPSTER-WORKBENCH', qty=10)
        product.allocate(line)
        uow.commit()

    batch_ref = get_allocated_batch_ref(session=session, order_id='o1', sku='HIPSTER-WORKBENCH')
    assert batch_ref == 'batch1'


def test_rolls_back_uncommitted_work_by_default(session_factory):
    with unit_of_work.SqlAlchemyUnitOfWork(session_factory) as uow:
        insert_batch(session=uow.session, ref='batch1', sku='MEDIUM-PLINTH', qty=100, eta=None)

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def test_rolls_back_on_error(session_factory):
    class MyException(Exception):
        pass

    with pytest.raises(MyException):
        with unit_of_work.SqlAlchemyUnitOfWork(session_factory) as uow:
            insert_batch(session=uow.session, ref='batch1', sku='LARGE-SPOON', qty=100, eta=None)
            raise MyException()

    new_session = session_factory()
    rows = list(new_session.execute(text('SELECT * FROM "batches"')))
    assert rows == []


def try_to_allocate(order_id, sku, exceptions):
    line = model.OrderLine(order_id=order_id, sku=sku, qty=10)
    try:
        with unit_of_work.SqlAlchemyUnitOfWork() as uow:
            product = uow.products.get(sku=sku)
            product.allocate(line)
            time.sleep(0.2)
            uow.commit()
    except Exception as e:
        print(traceback.format_exc())
        exceptions.append(e)


def test_concurrent_updates_to_version_are_not_allowed(postgres_session_factory):
    sku, batch = random_sku(), random_batch_ref()
    postgres_session = postgres_session_factory()
    insert_batch(session=postgres_session, ref=batch, sku=sku, qty=100, eta=None, product_version=1)
    postgres_session.commit()

    order1, order2 = random_order_id(1), random_order_id(2)
    exceptions = []  # type: list[Exception]
    thread1 = threading.Thread(target=lambda: try_to_allocate(order_id=order1, sku=sku, exceptions=exceptions))
    thread2 = threading.Thread(target=lambda: try_to_allocate(order_id=order2, sku=sku, exceptions=exceptions))
    thread1.start()
    thread2.start()
    thread1.join()
    thread2.join()

    [[version]] = postgres_session.execute(
        text('SELECT version_number FROM products WHERE sku=:sku'),
        dict(sku=sku),
    )
    assert version == 2
    [exception] = exceptions
    assert 'could not serialize access due to concurrent update' in str(exception)

    orders = postgres_session.execute(
        text(
            'SELECT order_id FROM allocations'
            ' JOIN batches ON allocations.batch_id = batches.id'
            ' JOIN order_lines ON allocations.orderline_id = order_lines.id'
            ' WHERE order_lines.sku=:sku'
        ),
        dict(sku=sku),
    )
    assert orders.rowcount == 1
    with unit_of_work.SqlAlchemyUnitOfWork() as uow:
        uow.session.execute(text('select 1'))
