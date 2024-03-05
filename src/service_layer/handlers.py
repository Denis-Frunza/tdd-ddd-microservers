from __future__ import annotations


from src.adapters.email import send_mail
from src.adapters import redis_eventpublisher
from src.domain import events, commands, model
from src.domain.exceptions import InvalidSku
from src.service_layer.unit_of_work import UnitOfWork


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    event: commands.Allocate,
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
    event: commands.CreateBatch,
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
    cmd: commands.ChangeBatchQuantity,
    uow: UnitOfWork,
):
    with uow:
        product = uow.products.get_by_batchref(batchref=cmd.ref)
        product.change_batch_quantity(ref=cmd.ref, qty=cmd.qty)
        uow.commit()


def publish_allocated_event(
    event: events.Allocated,
    uow: UnitOfWork,
):
    redis_eventpublisher.publish("line_allocated", event)


def send_out_of_stock_notification(event: events.OutOfStock, uow: UnitOfWork):
    send_mail(
        "stock@made.com",
        f"Out of stock for {event.sku}",
    )