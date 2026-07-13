import pytest

from dan.skills.skill import Skill


class TestSkill:
    def test_creation(self):
        skill = Skill(
            name="test_skill",
            description="A test skill",
            intent="test something",
            tool_name="echo",
        )
        assert skill.name == "test_skill"
        assert skill.tool_name == "echo"
        assert skill.success_count == 0
        assert skill.failure_count == 0

    def test_success_rate_empty(self):
        skill = Skill(
            name="s", description="d", intent="i", tool_name="t"
        )
        assert skill.success_rate == 0.0

    def test_success_rate(self):
        skill = Skill(
            name="s", description="d", intent="i", tool_name="t"
        )
        skill.success_count = 7
        skill.failure_count = 3
        assert skill.success_rate == 0.7

    def test_record_success(self):
        skill = Skill(
            name="s", description="d", intent="i", tool_name="t"
        )
        skill.record_success(0.9)
        assert skill.success_count == 1
        assert skill.avg_score == 0.9

    def test_record_success_multiple(self):
        skill = Skill(
            name="s", description="d", intent="i", tool_name="t"
        )
        skill.record_success(1.0)
        skill.record_success(0.6)
        assert skill.success_count == 2
        assert skill.avg_score == pytest.approx(0.8)

    def test_record_failure(self):
        skill = Skill(
            name="s", description="d", intent="i", tool_name="t"
        )
        skill.record_failure()
        assert skill.failure_count == 1

    def test_to_dict(self):
        skill = Skill(
            name="test",
            description="desc",
            intent="intent",
            tool_name="echo",
            examples=["say hi"],
        )
        data = skill.to_dict()
        assert data["name"] == "test"
        assert data["tool_name"] == "echo"
        assert data["examples"] == ["say hi"]

    def test_from_dict(self):
        data = {
            "name": "test",
            "description": "desc",
            "intent": "intent",
            "tool_name": "echo",
            "examples": ["hi"],
            "success_count": 5,
            "failure_count": 1,
            "avg_score": 0.85,
        }
        skill = Skill.from_dict(data)
        assert skill.name == "test"
        assert skill.success_count == 5
        assert skill.avg_score == 0.85

    def test_roundtrip(self):
        skill = Skill(
            name="rt",
            description="round trip",
            intent="test",
            tool_name="cmd",
            examples=["do thing"],
            success_count=3,
            failure_count=1,
            avg_score=0.75,
            metadata={"key": "val"},
        )
        data = skill.to_dict()
        restored = Skill.from_dict(data)
        assert restored.name == skill.name
        assert restored.success_count == skill.success_count
        assert restored.metadata == skill.metadata
