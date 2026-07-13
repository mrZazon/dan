import pytest

from dan.skills.registry import SkillRegistry
from dan.skills.skill import Skill


class TestSkillRegistry:
    @pytest.fixture
    def tmp_registry(self, tmp_path):
        return SkillRegistry(storage_path=tmp_path / "test_skills.json")

    def test_register_and_get(self, tmp_registry):
        skill = Skill(
            name="s1", description="d", intent="echo", tool_name="echo"
        )
        tmp_registry.register(skill)
        assert tmp_registry.get("s1") is skill

    def test_get_missing(self, tmp_registry):
        assert tmp_registry.get("nonexistent") is None

    def test_remove(self, tmp_registry):
        skill = Skill(
            name="s1", description="d", intent="i", tool_name="t"
        )
        tmp_registry.register(skill)
        assert tmp_registry.remove("s1") is True
        assert tmp_registry.get("s1") is None

    def test_remove_missing(self, tmp_registry):
        assert tmp_registry.remove("nonexistent") is False

    def test_list_skills(self, tmp_registry):
        s1 = Skill(name="s1", description="d1", intent="i1", tool_name="t1")
        s2 = Skill(name="s2", description="d2", intent="i2", tool_name="t2")
        tmp_registry.register(s1)
        tmp_registry.register(s2)
        skills = tmp_registry.list_skills()
        assert len(skills) == 2
        names = {s.name for s in skills}
        assert names == {"s1", "s2"}

    def test_names(self, tmp_registry):
        s1 = Skill(name="s1", description="d", intent="i", tool_name="t")
        tmp_registry.register(s1)
        assert tmp_registry.names() == ["s1"]

    def test_match_exact_intent(self, tmp_registry):
        skill = Skill(
            name="echo_skill",
            description="echoes",
            intent="echo",
            tool_name="echo",
        )
        tmp_registry.register(skill)
        result = tmp_registry.match("echo hello")
        assert result is skill

    def test_match_no_match(self, tmp_registry):
        skill = Skill(
            name="echo_skill",
            description="echoes",
            intent="echo",
            tool_name="echo",
        )
        tmp_registry.register(skill)
        result = tmp_registry.match("completely unrelated")
        assert result is None

    def test_match_uses_examples(self, tmp_registry):
        skill = Skill(
            name="weather",
            description="weather",
            intent="what is the",
            tool_name="weather",
            examples=["what is the temperature"],
        )
        skill.record_success(1.0)
        tmp_registry.register(skill)
        result = tmp_registry.match("what is the temperature outside")
        assert result is skill

    def test_match_better_score_wins(self, tmp_registry):
        s1 = Skill(
            name="loose",
            description="d",
            intent="zzz_no_match",
            tool_name="t1",
            examples=["hello world"],
        )
        s1.record_success(0.5)
        s2 = Skill(
            name="exact",
            description="d",
            intent="hello world",
            tool_name="t2",
        )
        s2.record_success(1.0)
        tmp_registry.register(s1)
        tmp_registry.register(s2)
        result = tmp_registry.match("hello world")
        assert result is not None
        assert result.name == "exact"

    def test_persistence(self, tmp_path):
        path = tmp_path / "skills.json"
        reg1 = SkillRegistry(storage_path=path)
        skill = Skill(
            name="persist", description="d", intent="i", tool_name="t"
        )
        reg1.register(skill)

        reg2 = SkillRegistry(storage_path=path)
        assert reg2.get("persist") is not None
        assert reg2.get("persist").name == "persist"

    def test_register_replaces(self, tmp_registry):
        s1 = Skill(
            name="s1", description="v1", intent="i", tool_name="t"
        )
        s2 = Skill(
            name="s1", description="v2", intent="i", tool_name="t"
        )
        tmp_registry.register(s1)
        tmp_registry.register(s2)
        assert tmp_registry.get("s1").description == "v2"
