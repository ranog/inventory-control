from datetime import date, timedelta

from src.v2.allocation.domain import events
from src.v2.allocation.domain.model import Batch, OrderLine, Product

today = date.today()
tomorrow = today + timedelta(days=1)
later = tomorrow + timedelta(days=10)


def test_prefers_warehouse_batches_to_shipments():
    in_stock_batch = Batch(ref='in-stock-batch', sku='RETRO-CLOCK', qty=100, eta=None)
    shipment_batch = Batch(ref='shipment-batch', sku='RETRO-CLOCK', qty=100, eta=tomorrow)
    product = Product(sku='RETRO-CLOCK', batches=[in_stock_batch, shipment_batch])
    line = OrderLine(order_id='order-123', sku='RETRO-CLOCK', qty=10)

    product.allocate(line)

    assert in_stock_batch.available_quantity == 90
    assert shipment_batch.available_quantity == 100


def test_prefers_earlier_batches():
    earliest = Batch(ref='speedy-batch', sku='MINIMALIST-SPOON', qty=100, eta=today)
    medium = Batch(ref='normal-batch', sku='MINIMALIST-SPOON', qty=100, eta=tomorrow)
    latest = Batch(ref='slow-batch', sku='MINIMALIST-SPOON', qty=100, eta=later)
    product = Product(sku='MINIMALIST-SPOON', batches=[medium, earliest, latest])
    line = OrderLine(order_id='order-123', sku='MINIMALIST-SPOON', qty=10)

    product.allocate(line)

    assert earliest.available_quantity == 90
    assert medium.available_quantity == 100
    assert latest.available_quantity == 100


def test_returns_allocated_batch_ref():
    in_stock_batch = Batch(ref='in-stock-batch', sku='HIGHBROW-POSTER', qty=100, eta=None)
    shipment_batch = Batch(ref='shipment-batch', sku='HIGHBROW-POSTER', qty=100, eta=tomorrow)
    line = OrderLine(order_id='order-123', sku='HIGHBROW-POSTER', qty=10)
    product = Product(sku='HIGHBROW-POSTER', batches=[in_stock_batch, shipment_batch])

    allocation = product.allocate(line)

    assert allocation == in_stock_batch.reference


def test_records_out_of_stock_event_if_cannot_allocate():
    batch = Batch(ref='batch1', sku='SMALL-FORK', qty=10, eta=today)
    product = Product(sku='SMALL-FORK', batches=[batch])
    product.allocate(OrderLine(order_id='order1', sku='SMALL-FORK', qty=10))

    allocation = product.allocate(OrderLine(order_id='order2', sku='SMALL-FORK', qty=1))

    assert product.events[-1] == events.OutOfStock(sku='SMALL-FORK')
    assert allocation is None


def test_increments_version_number():
    line = OrderLine(order_id='oref', sku='SCANDI-PEN', qty=10)
    product = Product(sku='SCANDI-PEN', batches=[Batch(ref='b1', sku='SCANDI-PEN', qty=100, eta=None)])
    product.version_number = 7

    product.allocate(line)

    assert product.version_number == 8
