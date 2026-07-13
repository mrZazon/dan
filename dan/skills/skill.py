from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any


@dataclass
class Skill:
    """A learned skill that maps user intent to tool execution."""

    name: str
    description: str
    intent: str
    tool_name: str
    args_template: dict[str, Any] = field(default_factory=dict)
    examples: list[str] = field(default_factory=list)
    created_at: float = field(default_factory=time.time)
    success_count: int = 0
    failure_count: int = 0
    avg_score: float = 0.0
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def success_rate(self) -> float:
        """Calculate success rate."""
        total = self.success_count + self.failure_count
        return self.success_count / total if total > 0 else 0.0

    def record_success(self, score: float = 1.0) -> None:
        """Record a successful execution."""
        self.success_count += 1
        total = self.success_count + self.failure_count
        self.avg_score = (
            (self.avg_score * (total - 1) + score) / total
            if total > 0
            else score
        )

    def record_failure(self) -> None:
        """Record a failed execution."""
        self.failure_count += 1

    def to_dict(self) -> dict[str, Any]:
        """Serialize to dictionary."""
        return {
            "name": self.name,
            "description": self.description,
            "intent": self.intent,
            "tool_name": self.tool_name,
            "args_template": self.args_template,
            "examples": self.examples,
            "created_at": self.created_at,
            "success_count": self.success_count,
            "failure_count": self.failure_count,
            "avg_score": self.avg_score,
            "metadata": self.metadata,
        }

    @classmethod
    def from_dict(cls, data: dict[str, Any]) -> Skill:
        """Deserialize from dictionary."""
        return cls(
            name=data["name"],
            description=data["description"],
            intent=data["intent"],
            tool_name=data["tool_name"],
            args_template=data.get("args_template", {}),
            examples=data.get("examples", []),
            created_at=data.get("created_at", time.time()),
            success_count=data.get("success_count", 0),
            failure_count=data.get("failure_count", 0),
            avg_score=data.get("avg_score", 0.0),
            metadata=data.get("metadata", {}),
        )
