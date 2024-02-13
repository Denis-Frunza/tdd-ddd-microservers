import typing as t
from datetime import date
from dataclasses import dataclass

class Event:
    ...


@dataclass
class OutOfStock(Event):
    sku: str
