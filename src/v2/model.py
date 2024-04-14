from dataclasses import dataclass
from datetime import date
from typing import Optional


@dataclass
class OrderLine:
    orderid: str
    sku: str  # stock-keeping unit
    qty: int


class Batch:
    def __init__(self, ref: str, sku: str, qty: int, eta: Optional[date]) -> None:
        self.referece = ref
        self.sku = sku
        self.available_quantity = qty
        self.eta = eta

    def allocate(self, line: OrderLine) -> None:
        self.available_quantity -= line.qty

    def can_allocate(self, line: OrderLine) -> bool:
        return self.sku == line.sku and self.available_quantity >= line.qty
