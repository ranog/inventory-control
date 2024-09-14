from sqlalchemy import text

from src.v2.allocation.domain import model


def test_orderline_mapper_can_load_lines(session):
    session.execute(
        text(
            'INSERT INTO order_lines (order_id, sku, qty) VALUES '
            '("order1", "RED-CHAIR", 12),'
            '("order1", "RED-TABLE", 13),'
            '("order2", "BLUE-LIPSTICK", 14)'
        ),
    )

    expected = [
        model.OrderLine('order1', 'RED-CHAIR', 12),
        model.OrderLine('order1', 'RED-TABLE', 13),
        model.OrderLine('order2', 'BLUE-LIPSTICK', 14),
    ]

    assert session.query(model.OrderLine).all() == expected


def test_orderline_mapper_can_save_lines(session):
    new_line = model.OrderLine('order1', 'DECORATIVE-WIDGET', 12)
    session.add(new_line)
    session.commit()

    rows = list(session.execute(text('SELECT order_id, sku, qty FROM "order_lines"')))

    assert rows == [('order1', 'DECORATIVE-WIDGET', 12)]


def test_batch_mapper_can_load_batches(session):
    session.execute(
        text(
            'INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES '
            "('batch1', 'sku1', 100, null),"
            "('batch2', 'sku2', 200, '2011-04-11'),"
            "('batch3', 'sku3', 300, '2011-05-12')"
        ),
    )

    expected = [
        model.Batch('batch1', 'sku1', 100, eta=None),
        model.Batch('batch2', 'sku2', 200, eta='2011-04-11'),
        model.Batch('batch3', 'sku3', 300, eta='2011-05-12'),
    ]

    assert session.query(model.Batch).all() == expected


def test_batch_mapper_can_save_batches(session):
    new_batch = model.Batch('batch1', 'sku1', 100, eta=None)
    session.add(new_batch)
    session.commit()

    rows = list(session.execute(text('SELECT reference, sku, _purchased_quantity, eta FROM "batches"')))

    assert rows == [('batch1', 'sku1', 100, None)]


def test_allocations_mapper_can_load_allocations(session):
    session.execute(text('INSERT INTO order_lines (order_id, sku, qty) VALUES ' "('order1', 'GENERIC-SOFA', 12)"))
    [[order_line_id]] = session.execute(
        text('SELECT id FROM order_lines WHERE order_id=:order_id AND sku=:sku'),
        dict(order_id='order1', sku='GENERIC-SOFA'),
    )

    session.execute(
        text(
            'INSERT INTO batches (reference, sku, _purchased_quantity, eta) VALUES '
            "('batch1', 'GENERIC-SOFA', 100, null)"
        ),
    )
    [[batch_id]] = session.execute(
        text('SELECT id FROM batches WHERE reference=:batch_id'),
        dict(batch_id='batch1'),
    )

    session.execute(
        text('INSERT INTO allocations (orderline_id, batch_id) VALUES (:orderline_id, :batch_id)'),
        dict(orderline_id=order_line_id, batch_id=batch_id),
    )

    expected = [(order_line_id, batch_id)]

    result = session.execute(text('SELECT orderline_id, batch_id FROM allocations')).fetchall()

    assert result == expected


def test_allocations_mapper_can_save_allocations(session):
    order_line = model.OrderLine('order1', 'GENERIC-SOFA', 12)
    batch = model.Batch('batch1', 'GENERIC-SOFA', 100, eta=None)
    batch.allocate(order_line)
    session.add(batch)
    session.commit()

    rows = list(session.execute(text('SELECT orderline_id, batch_id FROM allocations')))

    assert rows == [(order_line.id, batch.id)]
