import pytest

from dan.plugins.base import Plugin, PluginMetadata
from dan.plugins.registry import PluginRegistry


class MockPlugin(Plugin):
    def __init__(self, name="mock", version="0.1.0"):
        self._metadata = PluginMetadata(
            name=name, version=version, description="Mock plugin"
        )
        self.initialized = False
        self.shutdown_called = False

    async def initialize(self):
        self.initialized = True

    async def shutdown(self):
        self.shutdown_called = True

    def get_metadata(self):
        return self._metadata


class TestPluginMetadata:
    def test_creation(self):
        meta = PluginMetadata(name="test", version="1.0.0")
        assert meta.name == "test"
        assert meta.version == "1.0.0"
        assert meta.description == ""
        assert meta.dependencies == []

    def test_with_deps(self):
        meta = PluginMetadata(
            name="test",
            version="1.0",
            dependencies=["dep1", "dep2"],
        )
        assert meta.dependencies == ["dep1", "dep2"]


class TestPluginRegistry:
    @pytest.fixture
    def registry(self):
        return PluginRegistry()

    def test_register(self, registry):
        plugin = MockPlugin()
        registry.register(plugin)
        assert registry.get("mock") is plugin

    def test_get_missing(self, registry):
        assert registry.get("nonexistent") is None

    def test_remove(self, registry):
        plugin = MockPlugin()
        registry.register(plugin)
        assert registry.remove("mock") is True
        assert registry.get("mock") is None

    def test_remove_missing(self, registry):
        assert registry.remove("nonexistent") is False

    def test_list_plugins(self, registry):
        p1 = MockPlugin(name="p1")
        p2 = MockPlugin(name="p2")
        registry.register(p1)
        registry.register(p2)
        metas = registry.list_plugins()
        assert len(metas) == 2
        names = {m.name for m in metas}
        assert names == {"p1", "p2"}

    def test_names(self, registry):
        registry.register(MockPlugin(name="a"))
        assert registry.names() == ["a"]

    @pytest.mark.asyncio
    async def test_initialize_all(self, registry):
        plugin = MockPlugin()
        registry.register(plugin)
        await registry.initialize_all()
        assert plugin.initialized is True
        assert registry.is_initialized("mock") is True

    @pytest.mark.asyncio
    async def test_shutdown_all(self, registry):
        plugin = MockPlugin()
        registry.register(plugin)
        await registry.initialize_all()
        await registry.shutdown_all()
        assert plugin.shutdown_called is True
        assert registry.is_initialized("mock") is False

    @pytest.mark.asyncio
    async def test_initialize_only_uninitialized(self, registry):
        plugin = MockPlugin()
        registry.register(plugin)
        await registry.initialize_all()
        plugin.initialized = False
        await registry.initialize_all()
        # Should not re-init
        assert plugin.initialized is False

    def test_is_initialized_false_by_default(self, registry):
        registry.register(MockPlugin())
        assert registry.is_initialized("mock") is False

    def test_register_replaces(self, registry):
        p1 = MockPlugin(name="same", version="1.0")
        p2 = MockPlugin(name="same", version="2.0")
        registry.register(p1)
        registry.register(p2)
        assert registry.get("same").get_metadata().version == "2.0"

    @pytest.mark.asyncio
    async def test_initialize_exception_does_not_crash(self, registry):
        class BadPlugin(Plugin):
            async def initialize(self):
                raise RuntimeError("boom")

            async def shutdown(self):
                pass

            def get_metadata(self):
                return PluginMetadata(name="bad", version="0.1")

        registry.register(BadPlugin())
        await registry.initialize_all()
        assert registry.is_initialized("bad") is False
