from sqlalchemy import text

from src.v2.allocation.adapters import repository
from src.v2.allocation.domain import model


def test_repository_can_save_a_batch(session):
    batch = model.Batch(ref='batch-001', sku='RUSTY-SOAPDISH', qty=100, eta=None)
    repo = repository.SqlAlchemyRepository(session)

    repo.add(batch)

    session.commit()
    rows = session.execute(text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"'))

    assert list(rows) == [('batch-001', 'RUSTY-SOAPDISH', 100, None)]


def insert_order_line(session):
    session.execute(text('INSERT INTO order_lines (order_id, sku, qty) VALUES ' "('order1', 'GENERIC-SOFA', 12)"))
    [[order_line_id]] = session.execute(
        text('SELECT id FROM order_lines WHERE order_id=:order_id AND sku=:sku'),
        dict(order_id='order1', sku='GENERIC-SOFA'),
    )
    return order_line_id


def insert_batch(session, batch_id):
    session.execute(
        text(
            'INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES '
            "(:batch_id, 'GENERIC-SOFA', 100, null)"
        ),
        dict(batch_id=batch_id),
    )
    [[batch_id]] = session.execute(
        text('SELECT id FROM batches WHERE reference=:batch_id'),
        dict(batch_id=batch_id),
    )
    return batch_id


def insert_allocation(session, orderline_id, batch_id):
    session.execute(
        text('INSERT INTO allocations (orderline_id, batch_id) VALUES (:orderline_id, :batch_id)'),
        dict(orderline_id=orderline_id, batch_id=batch_id),
    )


def test_repository_can_retrieve_a_batch_with_allocations(session):
    orderline_id = insert_order_line(session)
    batch1_id = insert_batch(session=session, batch_id='batch1')
    insert_batch(session=session, batch_id='batch2')
    insert_allocation(session=session, orderline_id=orderline_id, batch_id=batch1_id)

    repo = repository.SqlAlchemyRepository(session)
    retrieved = repo.get('batch1')

    expected = model.Batch(ref='batch1', sku='GENERIC-SOFA', qty=100, eta=None)

    assert retrieved == expected
    assert retrieved.sku == expected.sku
    assert retrieved._purchased_quantity == expected._purchased_quantity
    assert retrieved._allocations == {model.OrderLine(order_id='order1', sku='GENERIC-SOFA', qty=12)}
