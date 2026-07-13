from __future__ import annotations

import logging
import time
from dataclasses import dataclass, field
from typing import Any

from dan.skills.skill import Skill

logger = logging.getLogger(__name__)


@dataclass
class ExecutionRecord:
    """Record of a tool execution for learning."""

    message: str
    tool_name: str
    args: dict[str, Any]
    success: bool
    score: float = 0.0
    duration: float = 0.0
    timestamp: float = field(default_factory=time.time)
    metadata: dict[str, Any] = field(default_factory=dict)


class LearningPipeline:
    """Compresses successful tool executions into reusable skills.

    This is the L3 layer of the D.A.N. architecture. It observes
    tool executions, identifies patterns, and creates skills from
    successful execution sequences.
    """

    def __init__(
        self,
        min_executions: int = 3,
        min_success_rate: float = 0.7,
    ) -> None:
        self._min_executions = min_executions
        self._min_success_rate = min_success_rate
        self._records: list[ExecutionRecord] = []

    def record(self, execution: ExecutionRecord) -> None:
        """Record a tool execution."""
        self._records.append(execution)
        logger.debug(
            "Recorded execution: %s (success=%s)",
            execution.tool_name,
            execution.success,
        )

    def get_patterns(self) -> list[dict[str, Any]]:
        """Analyze records and identify learnable patterns."""
        patterns: list[dict[str, Any]] = []

        # Group by tool name
        tool_groups: dict[str, list[ExecutionRecord]] = {}
        for record in self._records:
            if record.tool_name not in tool_groups:
                tool_groups[record.tool_name] = []
            tool_groups[record.tool_name].append(record)

        for tool_name, records in tool_groups.items():
            if len(records) < self._min_executions:
                continue

            success_count = sum(1 for r in records if r.success)
            success_rate = success_count / len(records)

            if success_rate < self._min_success_rate:
                continue

            # Find common message patterns
            messages = [r.message for r in records]
            common_intent = self._extract_common_intent(messages)

            if common_intent:
                patterns.append({
                    "tool_name": tool_name,
                    "intent": common_intent,
                    "success_rate": success_rate,
                    "execution_count": len(records),
                    "avg_score": sum(r.score for r in records) / len(records),
                })

        return patterns

    def generate_skills(self) -> list[Skill]:
        """Generate skills from identified patterns."""
        patterns = self.get_patterns()
        skills: list[Skill] = []

        for pattern in patterns:
            skill = Skill(
                name=f"learned_{pattern['tool_name']}_{len(skills)}",
                description=f"Learned skill for {pattern['tool_name']} "
                f"(success rate: {pattern['success_rate']:.1%})",
                intent=pattern["intent"],
                tool_name=pattern["tool_name"],
                examples=self._get_examples_for_tool(pattern["tool_name"]),
                metadata={
                    "learned_from": "pipeline",
                    "success_rate": pattern["success_rate"],
                    "execution_count": pattern["execution_count"],
                },
            )
            skills.append(skill)

        return skills

    def _extract_common_intent(self, messages: list[str]) -> str | None:
        """Extract common intent from a list of messages."""
        if not messages:
            return None

        # Simple approach: find most common words
        word_counts: dict[str, int] = {}
        for message in messages:
            words = message.lower().split()
            for word in words:
                if len(word) > 2:  # Skip short words
                    word_counts[word] = word_counts.get(word, 0) + 1

        if not word_counts:
            return None

        # Get most common words
        sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)
        top_words = [word for word, count in sorted_words[:3]]

        return " ".join(top_words) if top_words else None

    def _get_examples_for_tool(self, tool_name: str) -> list[str]:
        """Get example messages for a tool."""
        examples = []
        for record in self._records:
            if record.tool_name == tool_name and record.success:
                examples.append(record.message)
                if len(examples) >= 3:
                    break
        return examples

    def clear_old_records(self, max_age_seconds: float = 86400) -> int:
        """Clear records older than max_age_seconds."""
        cutoff = time.time() - max_age_seconds
        original_count = len(self._records)
        self._records = [r for r in self._records if r.timestamp > cutoff]
        return original_count - len(self._records)
