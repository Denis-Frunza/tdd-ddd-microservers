import typing as t
from datetime import date
from dataclasses import dataclass

class Command:
    ...


@dataclass
class Allocate(Command):
    orderid: str
    sku: str
    qty: int


@dataclass
class CreateBatch(Command):
    ref: str
    sku: str
    qty: int
    eta: t.Optional[date] = None


@dataclass
class ChangeBatchQuantity(Command):
    ref: str
    qty: int
