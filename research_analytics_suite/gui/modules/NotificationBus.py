"""
NotificationBus Module

Central event bus for publishing and subscribing to GUI notifications across the application.
Implements singleton pattern to ensure a single event bus instance.

Author: Lane
Copyright: Lane
Credits: Lane
License: BSD 3-Clause License
Version: 0.0.0.1
Maintainer: Lane
Email: justlane@uw.edu
Status: Prototype
"""

import asyncio
from typing import Callable, Dict, List, Any
from collections import defaultdict


class NotificationBus:
    _instance = None
    _lock = asyncio.Lock()

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self._event_queue: asyncio.Queue = asyncio.Queue()
        self._processing_task = None
        self._is_running = False
        self._initialized = True

    async def start(self):
        """Start processing events from the queue."""
        if self._is_running and self._processing_task and not self._processing_task.done():
            return

        self._is_running = True
        self._processing_task = asyncio.create_task(self._process_events())

    async def stop(self):
        """Stop processing events and clean up."""
        self._is_running = False
        if self._processing_task and not self._processing_task.done():
            self._processing_task.cancel()
            try:
                await self._processing_task
            except asyncio.CancelledError:
                pass
        self._processing_task = None

    async def _process_events(self):
        """Internal event processing loop."""
        while self._is_running:
            try:
                event_type, data = await asyncio.wait_for(
                    self._event_queue.get(), timeout=0.1
                )
                await self._notify_subscribers(event_type, data)
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                from research_analytics_suite.utils import CustomLogger
                CustomLogger().error(e, self.__class__.__name__)

    async def _notify_subscribers(self, event_type: str, data: Dict[str, Any]):
        """Notify all subscribers of an event type."""
        if event_type in self._subscribers:
            for callback in self._subscribers[event_type]:
                try:
                    if asyncio.iscoroutinefunction(callback):
                        await callback(data)
                    else:
                        callback(data)
                except Exception as e:
                    from research_analytics_suite.utils import CustomLogger
                    CustomLogger().error(
                        Exception(f"Error in notification callback for {event_type}: {e}"),
                        self.__class__.__name__
                    )

    def subscribe(self, event_type: str, callback: Callable):
        """
        Subscribe to an event type.

        Args:
            event_type: The type of event to subscribe to
            callback: The callback function to invoke when event is published
        """
        if callback not in self._subscribers[event_type]:
            self._subscribers[event_type].append(callback)

    def unsubscribe(self, event_type: str, callback: Callable):
        """
        Unsubscribe from an event type.

        Args:
            event_type: The type of event to unsubscribe from
            callback: The callback function to remove
        """
        if event_type in self._subscribers and callback in self._subscribers[event_type]:
            self._subscribers[event_type].remove(callback)

    def publish(self, event_type: str, data: Dict[str, Any]):
        """
        Publish an event to all subscribers.

        Args:
            event_type: The type of event being published
            data: Data associated with the event
        """
        try:
            self._event_queue.put_nowait((event_type, data))
        except Exception as e:
            from research_analytics_suite.utils import CustomLogger
            CustomLogger().error(
                Exception(f"Error publishing event {event_type}: {e}"),
                self.__class__.__name__
            )

    def clear_subscribers(self, event_type: str = None):
        """
        Clear all subscribers for a specific event type, or all subscribers if no type specified.

        Args:
            event_type: Optional specific event type to clear
        """
        if event_type:
            self._subscribers[event_type].clear()
        else:
            self._subscribers.clear()

    async def reset(self):
        """Reset the notification bus to initial state."""
        await self.stop()
        await asyncio.sleep(0.05)
        self.clear_subscribers()

        while not self._event_queue.empty():
            try:
                self._event_queue.get_nowait()
            except asyncio.QueueEmpty:
                break

        self._event_queue = asyncio.Queue()
        self._is_running = False
        self._processing_task = None


notification_bus = NotificationBus()
