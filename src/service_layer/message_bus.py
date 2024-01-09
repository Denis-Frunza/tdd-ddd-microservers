from typing import List, Dict, Callable, Type
from src.adapters import email
from src.domain import events

def handle(event: events.Event):
    for handler in HANDLERS[type(event)]:
        handler(event)


def send_out_of_stock_notification(event: events.OutOfStock):
    email.send_mail(
    'stock@made.com',
    f'out of stock {event.sku} ',
    )


HANDLERS: Dict[Type[events.Event], List[Callable]] = {
    events.OutOfStock: [send_out_of_stock_notification],
}