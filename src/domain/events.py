import typing as t
from datetime import date
from dataclasses import dataclass

class Event:
    ...


@dataclass
class OutOfStock(Event):
    sku: str


@dataclass
class BatchCreated(Event):
    ref: str
    sku: str
    qty: int
    eta: t.Optional[date] = None


@dataclass
class AllocationRequired(Event):
    orderid: str
    sku: str
    qty: int


@dataclass
class BatchQuantityChanged(Event):
    ref: str
    qty: int