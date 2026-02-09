"""
Test NotificationBus functionality

Author: Lane
"""

import asyncio
import pytest
from research_analytics_suite.gui.modules import NotificationBus


class TestNotificationBus:
    """Test cases for NotificationBus event system."""

    @pytest.fixture(autouse=True)
    async def reset_bus(self):
        """Reset the notification bus before each test."""
        bus = NotificationBus()
        await bus.reset()
        yield
        await bus.reset()

    def test_singleton_pattern(self):
        """Test that NotificationBus implements singleton pattern."""
        bus1 = NotificationBus()
        bus2 = NotificationBus()
        assert bus1 is bus2

    @pytest.mark.asyncio
    async def test_subscribe_and_publish(self):
        """Test basic subscribe and publish functionality."""
        bus = NotificationBus()
        await bus.start()

        received_events = []

        def callback(data):
            received_events.append(data)

        bus.subscribe("test_event", callback)
        bus.publish("test_event", {"message": "test"})

        await asyncio.sleep(0.2)

        assert len(received_events) == 1
        assert received_events[0]["message"] == "test"

    @pytest.mark.asyncio
    async def test_multiple_subscribers(self):
        """Test multiple subscribers to same event."""
        bus = NotificationBus()
        await bus.start()

        counter = {"count": 0}

        def callback1(data):
            counter["count"] += 1

        def callback2(data):
            counter["count"] += 10

        bus.subscribe("multi_test", callback1)
        bus.subscribe("multi_test", callback2)
        bus.publish("multi_test", {})

        await asyncio.sleep(0.2)

        assert counter["count"] == 11

    @pytest.mark.asyncio
    async def test_unsubscribe(self):
        """Test unsubscribe functionality."""
        bus = NotificationBus()
        await bus.start()

        received = []

        def callback(data):
            received.append(data)

        bus.subscribe("unsub_test", callback)
        bus.publish("unsub_test", {"value": 1})

        await asyncio.sleep(0.2)

        bus.unsubscribe("unsub_test", callback)
        bus.publish("unsub_test", {"value": 2})

        await asyncio.sleep(0.2)

        assert len(received) == 1
        assert received[0]["value"] == 1

    @pytest.mark.asyncio
    async def test_async_callback(self):
        """Test async callback functions."""
        bus = NotificationBus()
        await bus.start()

        received = []

        async def async_callback(data):
            await asyncio.sleep(0.1)
            received.append(data)

        bus.subscribe("async_test", async_callback)
        bus.publish("async_test", {"async": True})

        await asyncio.sleep(0.3)

        assert len(received) == 1
        assert received[0]["async"] is True
