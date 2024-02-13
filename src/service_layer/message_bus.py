import logging

from typing import Callable, Dict, List, Type, Union

from src.domain import events
from src.service_layer import handlers
from src.service_layer.unit_of_work import UnitOfWork
from src.domain import commands


logger = logging.getLogger(__name__)

Message = Union[commands.Command, events.Event]


def handle(
    message: Message,
    uow: UnitOfWork,
):
    results = []
    queue = [message]
    while queue:
        message = queue.pop(0)
        if isinstance(message, events.Event):
            handle_event(message, queue, uow)
        elif isinstance(message, commands.Command):
            cmd_result = handle_command(message, queue, uow)
            results.append(cmd_result)
        else:
            raise Exception(f"{message} was not an Event or Command")
    return results



def handle_event(
    event: events.Event,
    queue: List[Message],
    uow: UnitOfWork,
):
    for handler in EVENT_HANDLERS[type(event)]:
        try:
            logger.debug("handling event %s with handler %s", event, handler)
            handler(event, uow=uow)
            queue.extend(uow.collect_new_events())
        except Exception:
            logger.exception("Exception handling event %s", event)
            continue

def handle_command(
    command: commands.Command,
    queue: List[Message],
    uow: UnitOfWork,
):
    logger.debug("handling command %s", command)
    try:
        handler = COMMAND_HANDLERS[type(command)]
        result = handler(command, uow=uow)
        queue.extend(uow.collect_new_events())
        return result
    except Exception:
        logger.exception("Exception handling command %s", command)
        raise


EVENT_HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.OutOfStock: [handlers.send_out_of_stock_notification],
}

COMMAND_HANDLERS: Dict[Type[commands.Command], List[Callable]] = {
    commands.Allocate: handlers.allocate,
    commands.CreateBatch: handlers.add_batch,
    commands.ChangeBatchQuantity: handlers.change_batch_quantity,
}
