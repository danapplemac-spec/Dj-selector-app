from __future__ import annotations

from collections import defaultdict
from dataclasses import dataclass
from typing import Any, Callable


@dataclass
class Event:
    name: str
    payload: dict[str, Any]


class EventBus:
    def __init__(self) -> None:
        self._listeners: dict[str, list[Callable[[Event], None]]] = defaultdict(list)

    def subscribe(self, event_name: str, listener: Callable[[Event], None]) -> None:
        self._listeners[event_name].append(listener)

    def emit(self, event_name: str, **payload: Any) -> None:
        event = Event(name=event_name, payload=payload)
        for listener in self._listeners[event_name]:
            listener(event)
        for listener in self._listeners["*"]:
            listener(event)
