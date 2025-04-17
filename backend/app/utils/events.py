"""
Domain Events Module

This module provides domain event infrastructure for the application.
Domain events represent significant occurrences in the domain model
that other parts of the application might need to react to.
"""

from abc import ABC
from typing import List, Callable, Dict, Any
from dataclasses import dataclass, field


class DomainEvent(ABC):
    """Base class for all domain events."""
    pass


class EventBus:
    """
    Event bus for publishing and subscribing to domain events.
    
    This allows for loose coupling between components that generate events
    and those that need to react to them.
    """
    
    def __init__(self):
        self._handlers: Dict[type, List[Callable]] = {}
        
    def subscribe(self, event_type: type, handler: Callable) -> None:
        """
        Subscribe a handler to a specific event type.
        
        Args:
            event_type: The type of event to subscribe to
            handler: The function that will handle the event
        """
        if event_type not in self._handlers:
            self._handlers[event_type] = []
        self._handlers[event_type].append(handler)
        
    def publish(self, event: DomainEvent) -> None:
        """
        Publish an event to all subscribed handlers.
        
        Args:
            event: The event to publish
        """
        event_type = type(event)
        if event_type in self._handlers:
            for handler in self._handlers[event_type]:
                handler(event)


# Global event bus instance for application-wide use
event_bus = EventBus() 