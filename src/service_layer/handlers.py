from __future__ import annotations

from datetime import date
from typing import Optional

from src.adapters.email import send_mail
from src.domain import model
from src.domain import events
from src.domain.exceptions import InvalidSku
from src.service_layer.unit_of_work import UnitOfWork


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    event: events.AllocationRequired,
    uow: UnitOfWork,
) -> str:
    line = model.OrderLine(event.orderid, event.sku, event.qty)
    with uow:
        product = uow.products.get(sku=line.sku)
        if product is None:
            raise InvalidSku(f"Invalid sku {line.sku}")
        batchref = product.allocate(line)
        uow.commit()
    return batchref


def add_batch(
    event: events.BatchCreated,
    uow: UnitOfWork,
):
    with uow:
        product = uow.products.get(sku=event.sku)
        if product is None:
            product = model.Product(event.sku, batches=[])
            uow.products.add(product)
        product.batches.append(model.Batch(event.ref, event.sku, event.qty, event.eta))
        uow.commit()

def change_batch_quantity(
    event: events.BatchQuantityChanged,
    uow: UnitOfWork,
):
    with uow:
        product = uow.products.get_by_batchref(batchref=event.ref)
        product.change_batch_quantity(ref=event.ref, qty=event.qty)
        uow.commit()


def send_out_of_stock_notification(event: events.OutOfStock, uow: UnitOfWork):
    send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )