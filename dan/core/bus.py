from __future__ import annotations

import logging
from collections import defaultdict
from collections.abc import Callable, Coroutine
from dataclasses import dataclass, field
from typing import Any

logger = logging.getLogger(__name__)

EventHandler = Callable[..., Coroutine[Any, Any, None]]


@dataclass
class Event:
    """An event published to the bus."""

    topic: str
    data: dict[str, Any] = field(default_factory=dict)
    source: str = ""


class EventBus:
    """In-process publish/subscribe event bus.

    Enables loose coupling between components.
    All internal communication should prefer events.
    """

    def __init__(self) -> None:
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)
        self._history: list[Event] = []

    def subscribe(self, topic: str, handler: EventHandler) -> None:
        """Subscribe a handler to a topic.

        Args:
            topic: Event topic (e.g., "tool.executed").
            handler: Async callable to invoke when event is published.
        """
        self._handlers[topic].append(handler)
        logger.debug("Subscribed to '%s': %s", topic, handler.__qualname__)

    def unsubscribe(self, topic: str, handler: EventHandler) -> None:
        """Unsubscribe a handler from a topic."""
        handlers = self._handlers.get(topic, [])
        if handler in handlers:
            handlers.remove(handler)
            logger.debug("Unsubscribed from '%s': %s", topic, handler.__qualname__)

    async def publish(self, topic: str, source: str = "", **data: Any) -> Event:
        """Publish an event to all subscribed handlers.

        Args:
            topic: Event topic.
            source: Component that published the event.
            **data: Event payload.

        Returns:
            The published Event.
        """
        event = Event(topic=topic, data=data, source=source)
        self._history.append(event)

        handlers = self._handlers.get(topic, [])
        if not handlers:
            return event

        logger.debug("Publishing '%s' from '%s' to %d handlers", topic, source, len(handlers))

        for handler in handlers:
            try:
                await handler(**data)
            except Exception:
                logger.exception("Handler %s failed for event '%s'", handler.__qualname__, topic)

        return event

    def history(self, topic: str | None = None, limit: int = 100) -> list[Event]:
        """Return event history, optionally filtered by topic."""
        if topic is None:
            return list(self._history[-limit:])
        return [e for e in self._history if e.topic == topic][-limit:]

    def clear_history(self) -> None:
        """Clear event history."""
        self._history.clear()
