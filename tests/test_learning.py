import time

import pytest

from dan.learn.pipeline import ExecutionRecord, LearningPipeline


class TestExecutionRecord:
    def test_creation(self):
        rec = ExecutionRecord(
            message="echo hello",
            tool_name="echo",
            args={"message": "hello"},
            success=True,
            score=1.0,
        )
        assert rec.message == "echo hello"
        assert rec.success is True
        assert rec.score == 1.0

    def test_default_values(self):
        rec = ExecutionRecord(
            message="test",
            tool_name="cmd",
            args={},
            success=False,
        )
        assert rec.success is False
        assert rec.timestamp > 0
        assert rec.metadata == {}


class TestLearningPipeline:
    @pytest.fixture
    def pipeline(self):
        return LearningPipeline(min_executions=3, min_success_rate=0.7)

    def _make_records(self, n, tool_name="echo", success_rate=1.0):
        records = []
        for i in range(n):
            success = (i / max(n - 1, 1)) < success_rate
            records.append(
                ExecutionRecord(
                    message=f"echo message {i}",
                    tool_name=tool_name,
                    args={"message": f"msg {i}"},
                    success=success,
                    score=1.0 if success else 0.0,
                )
            )
        return records

    def test_record(self, pipeline):
        rec = ExecutionRecord(
            message="test", tool_name="cmd", args={}, success=True
        )
        pipeline.record(rec)
        assert len(pipeline._records) == 1

    def test_patterns_insufficient_executions(self, pipeline):
        for rec in self._make_records(2):
            pipeline.record(rec)
        patterns = pipeline.get_patterns()
        assert len(patterns) == 0

    def test_patterns_low_success_rate(self, pipeline):
        for rec in self._make_records(5, success_rate=0.3):
            pipeline.record(rec)
        patterns = pipeline.get_patterns()
        assert len(patterns) == 0

    def test_patterns_found(self, pipeline):
        for rec in self._make_records(5, success_rate=1.0):
            pipeline.record(rec)
        patterns = pipeline.get_patterns()
        assert len(patterns) == 1
        assert patterns[0]["tool_name"] == "echo"

    def test_generate_skills(self, pipeline):
        for rec in self._make_records(5, success_rate=1.0):
            pipeline.record(rec)
        skills = pipeline.generate_skills()
        assert len(skills) == 1
        assert skills[0].tool_name == "echo"
        assert skills[0].name.startswith("learned_echo")

    def test_generate_skills_empty(self, pipeline):
        skills = pipeline.generate_skills()
        assert len(skills) == 0

    def test_multiple_tool_patterns(self, pipeline):
        for rec in self._make_records(4, tool_name="echo", success_rate=1.0):
            pipeline.record(rec)
        for rec in self._make_records(4, tool_name="cmd", success_rate=1.0):
            pipeline.record(rec)
        patterns = pipeline.get_patterns()
        tool_names = {p["tool_name"] for p in patterns}
        assert "echo" in tool_names
        assert "cmd" in tool_names

    def test_clear_old_records(self, pipeline):
        rec1 = ExecutionRecord(
            message="old",
            tool_name="cmd",
            args={},
            success=True,
            timestamp=time.time() - 200000,
        )
        rec2 = ExecutionRecord(
            message="new",
            tool_name="cmd",
            args={},
            success=True,
            timestamp=time.time(),
        )
        pipeline.record(rec1)
        pipeline.record(rec2)
        removed = pipeline.clear_old_records(max_age_seconds=100000)
        assert removed == 1
        assert len(pipeline._records) == 1

    def test_skills_have_examples(self, pipeline):
        for i in range(5):
            pipeline.record(
                ExecutionRecord(
                    message=f"echo test {i}",
                    tool_name="echo",
                    args={},
                    success=True,
                )
            )
        skills = pipeline.generate_skills()
        assert len(skills) == 1
        assert len(skills[0].examples) > 0
