from __future__ import annotations
from typing import Optional
from datetime import date

from src.domain.exceptions import InvalidSku
from src.domain import model
from src.service_layer.unit_of_work import UnitOfWork


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    orderid: str, sku: str, qty: int,
    uow: UnitOfWork,
) -> str:
    line = model.OrderLine(orderid, sku, qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = product.allocate(line)
        uow.commit()
    return batchref


def add_batch(
    ref: str, sku: str, qty: int, eta: Optional[date],
    uow: UnitOfWork,
):
    with uow:
        product = uow.products.get(sku=sku)
        if product is None:
            product = model.Product(sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(ref, sku, qty, eta))
        uow.commit()