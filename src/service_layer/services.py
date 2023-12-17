import typing as t
from datetime import date

from src.domain.exceptions import InvalidSku
from src.domain import model
from src.adapters.repository import AbstractRepository


def is_valid_sku(sku, batches):
    return sku in {b.sku for b in batches}


def allocate(
    orderid: str, sku: str, qty: int, repo: AbstractRepository, session
) -> str:

    line = model.OrderLine(orderid, sku, qty)
    batches = repo.list()
    if not is_valid_sku(line.sku, batches): 
        raise InvalidSku(f'Wrong {line.sku}')

    batchref = model.allocate(line, batches) 
    session.commit() 
    return batchref


def add_batch(
    ref: str, sku: str, qty: int, eta: t.Optional[date],
    repo: AbstractRepository, session,
):
    repo.add(model.Batch(ref, sku, qty, eta))
    session.commit()