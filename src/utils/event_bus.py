import threading
from collections import defaultdict
from typing import Any, Callable, Dict, List, Type, TypeVar

T = TypeVar('T')

class EventBus:
    """
    A simple, thread-safe event bus for subscribing to and firing events.
    Handlers are called synchronously in the order they were added.
    """
    def __init__(self):
        self._subscribers: Dict[Type[Any], List[Callable[[Any], None]]] = defaultdict(list)
        self._lock = threading.Lock()

    def subscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        """
        Subscribe a handler to a specific event type.
        """
        with self._lock:
            self._subscribers[event_type].append(handler)

    def unsubscribe(self, event_type: Type[T], handler: Callable[[T], None]) -> None:
        """
        Unsubscribe a handler from a specific event type.
        """
        with self._lock:
            if handler in self._subscribers[event_type]:
                self._subscribers[event_type].remove(handler)

    def fire(self, event: Any) -> None:
        """
        Fire an event, calling all subscribed handlers for its type.
        """
        handlers = []
        with self._lock:
            handlers = list(self._subscribers[type(event)])
        for handler in handlers:
            handler(event) 