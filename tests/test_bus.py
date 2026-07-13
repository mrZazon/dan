import pytest

from dan.core.bus import Event, EventBus


class TestEventBus:
    @pytest.fixture
    def bus(self):
        return EventBus()

    @pytest.mark.asyncio
    async def test_publish_subscribe(self, bus):
        received = []

        async def handler(**kwargs):
            received.append(kwargs)

        bus.subscribe("test.topic", handler)
        await bus.publish("test.topic", key="value")

        assert len(received) == 1
        assert received[0]["key"] == "value"

    @pytest.mark.asyncio
    async def test_multiple_handlers(self, bus):
        count = {"a": 0, "b": 0}

        async def handler_a(**kwargs):
            count["a"] += 1

        async def handler_b(**kwargs):
            count["b"] += 1

        bus.subscribe("test", handler_a)
        bus.subscribe("test", handler_b)
        await bus.publish("test")

        assert count["a"] == 1
        assert count["b"] == 1

    @pytest.mark.asyncio
    async def test_unsubscribe(self, bus):
        received = []

        async def handler(**kwargs):
            received.append(True)

        bus.subscribe("test", handler)
        bus.unsubscribe("test", handler)
        await bus.publish("test")

        assert len(received) == 0

    @pytest.mark.asyncio
    async def test_publish_returns_event(self, bus):
        event = await bus.publish("test.topic", source="test", foo="bar")
        assert isinstance(event, Event)
        assert event.topic == "test.topic"
        assert event.data["foo"] == "bar"
        assert event.source == "test"

    @pytest.mark.asyncio
    async def test_handler_exception_does_not_break(self, bus):
        async def bad_handler(**kwargs):
            raise RuntimeError("boom")

        async def good_handler(**kwargs):
            pass

        bus.subscribe("test", bad_handler)
        bus.subscribe("test", good_handler)

        # Should not raise
        await bus.publish("test")

    def test_history(self, bus):
        import asyncio

        asyncio.run(bus.publish("a", x=1))
        asyncio.run(bus.publish("b", x=2))
        asyncio.run(bus.publish("a", x=3))

        all_events = bus.history()
        assert len(all_events) == 3

        a_events = bus.history(topic="a")
        assert len(a_events) == 2

    def test_clear_history(self, bus):
        import asyncio

        asyncio.run(bus.publish("test"))
        bus.clear_history()
        assert len(bus.history()) == 0
