import pytest

from dan.core.router import Layer, Route, Router
from dan.core.tool_registry import ToolRegistry


class TestRoute:
    def test_creation(self):
        route = Route(layer=Layer.REFLEX, tool_name="echo", confidence=1.0)
        assert route.layer == Layer.REFLEX
        assert route.tool_name == "echo"
        assert route.confidence == 1.0

    def test_defaults(self):
        route = Route(layer=Layer.INTERPRET)
        assert route.tool_name is None
        assert route.confidence == 0.0
        assert route.args == {}


class TestLayer:
    def test_ordering(self):
        assert Layer.REFLEX < Layer.INTERPRET < Layer.REASON < Layer.LEARN

    def test_values(self):
        assert Layer.REFLEX == 0
        assert Layer.INTERPRET == 1
        assert Layer.REASON == 2
        assert Layer.LEARN == 3


class TestRouter:
    @pytest.fixture
    def registry(self):
        reg = ToolRegistry()
        reg.discover()
        return reg

    def test_l0_skill_match(self, registry):
        from dan.skills.registry import SkillRegistry
        from dan.skills.skill import Skill

        skill_registry = SkillRegistry()
        skill = Skill(
            name="echo_skill",
            description="echo skill",
            intent="echo",
            tool_name="echo",
            examples=["echo this"],
        )
        skill_registry.register(skill)

        router = Router(
            registry=registry, skill_registry=skill_registry, threshold=0.5
        )
        import asyncio
        route = asyncio.run(router.route("echo hello world"))
        assert route.layer == Layer.LEARN
        assert route.skill_name == "echo_skill"

    def test_l0_no_match_below_threshold(self, registry):
        router = Router(registry=registry, threshold=5.0)
        import asyncio
        route = asyncio.run(router.route("echo hello"))
        # No layer matched above threshold
        assert route.confidence < 5.0

    def test_no_interpret_without_provider(self, registry):
        router = Router(registry=registry, threshold=5.0)
        import asyncio
        route = asyncio.run(router.route("echo hello"))
        # No interpret provider, no match above threshold
        assert route.layer == Layer.REFLEX
        assert route.confidence < 5.0

    def test_custom_threshold(self, registry):
        router = Router(registry=registry, threshold=0.0)
        import asyncio
        route = asyncio.run(router.route("echo hello"))
        assert route.confidence >= 0.0
