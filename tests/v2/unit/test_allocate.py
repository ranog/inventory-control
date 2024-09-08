from datetime import date, timedelta

import pytest

from src.v2.allocation.domain.model import Batch, OrderLine, allocate, OutOfStock

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_current_stock_batches_to_shipments():
    in_stock_batch = Batch(ref='in-stock-batch', sku='RETRO-CLOCK', qty=100, eta=None)
    shipment_batch = Batch(ref='shipment-batch', sku='RETRO-CLOCK', qty=100, eta=tomorrow)
    line = OrderLine(order_id='order-123', sku='RETRO-CLOCK', qty=10)

    allocate(line, [in_stock_batch, shipment_batch])

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch(ref='speedy-batch', sku='MINIMALIST-SPOON', qty=100, eta=today)
    medium = Batch(ref='normal-batch', sku='MINIMALIST-SPOON', qty=100, eta=tomorrow)
    latest = Batch(ref='slow-batch', sku='MINIMALIST-SPOON', qty=100, eta=later)
    line = OrderLine(order_id='order-123', sku='MINIMALIST-SPOON', qty=10)

    allocate(line, [medium, earliest, latest])

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch(ref='in-stock-batch', sku='HIGHBROW-POSTER', qty=100, eta=None)
    shipment_batch = Batch(ref='shipment-batch', sku='HIGHBROW-POSTER', qty=100, eta=tomorrow)
    line = OrderLine(order_id='order-123', sku='HIGHBROW-POSTER', qty=10)

    allocation = allocate(line, [in_stock_batch, shipment_batch])

    assert allocation == in_stock_batch.reference


def test_raises_out_of_stock_exception_if_cannot_allocate():
    batch = Batch(ref='batch1', sku='SMALL-FORK', qty=10, eta=today)
    allocate(line=OrderLine(order_id='order-123', sku='SMALL-FORK', qty=10), batches=[batch])

    with pytest.raises(OutOfStock, match='SMALL-FORK') as error:
        allocate(line=OrderLine(order_id='order-456', sku='SMALL-FORK', qty=1), batches=[batch])

    assert str(error.value) == 'Out of stock for sku SMALL-FORK'
