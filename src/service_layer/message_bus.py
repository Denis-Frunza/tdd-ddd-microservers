from typing import Callable, Dict, List, Type

from src.domain import events
from src.service_layer import handlers
from src.service_layer.unit_of_work import UnitOfWork


def handle(
    event: events.Event,
    uow: UnitOfWork,
):
    results = []
    queue = [event]
    while queue:
        event = queue.pop(0)
        for handler in HANDLERS[type(event)]:
            results.append(handler(event, uow=uow))
            queue.extend(uow.collect_new_events())
    return results


HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.BatchCreated: [handlers.add_batch],
    events.BatchQuantityChanged: [handlers.change_batch_quantity],
    events.AllocationRequired: [handlers.allocate],
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}
