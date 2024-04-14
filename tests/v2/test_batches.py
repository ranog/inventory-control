from datetime import date

from src.v2.model import Batch, OrderLine


def test_allocating_to_a_batch_reduces_the_available_quantity():
    batch = Batch(ref='batch-001', sku='STEPPER-MOTOR', qty=20, eta=date.today())
    line = OrderLine(orderid='order-ref', sku='STEPPER-MOTOR', qty=2)

    batch.allocate(line)

    assert batch.available_quantity == 18


def test_can_allocate_if_available_greater_than_required():
    batch = Batch(ref='batch-001', sku='STEPPER-MOTOR', qty=20, eta=date.today())
    line = OrderLine(orderid='order-ref', sku='STEPPER-MOTOR', qty=2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_available_smaller_than_required():
    batch = Batch(ref='batch-001', sku='STEPPER-MOTOR', qty=2, eta=date.today())
    line = OrderLine(orderid='order-ref', sku='STEPPER-MOTOR', qty=20)

    assert not batch.can_allocate(line)


def test_can_allocate_if_available_equal_to_required():
    batch = Batch(ref='batch-001', sku='STEPPER-MOTOR', qty=2, eta=date.today())
    line = OrderLine(orderid='order-ref', sku='STEPPER-MOTOR', qty=2)

    assert batch.can_allocate(line)


def test_cannot_allocate_if_skus_do_not_match():
    batch = Batch(ref='batch-001', sku='STEPPER-MOTOR', qty=20, eta=None)
    line = OrderLine(orderid='order-ref', sku='MICRO-SERVO-9G-SG90', qty=2)

    assert not batch.can_allocate(line)


def test_can_only_deallocate_allocated_lines():
    batch = Batch(ref='batch-001', sku='STEPPER-MOTOR', qty=20, eta=date.today())
    line = OrderLine(orderid='order-ref', sku='STEPPER-MOTOR', qty=2)

    batch.deallocate(line)

    assert batch.available_quantity == 20
