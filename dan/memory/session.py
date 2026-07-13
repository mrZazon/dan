from __future__ import annotations

import logging
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)

MAX_HISTORY = 20


@dataclass
class Turn:
    role: str
    content: str


@dataclass
class SessionMemory:
    """In-memory conversation history for a single session.

    Stores the last N turns so the LLM gets context about what
    was said and done previously.
    """

    history: list[Turn] = field(default_factory=list)
    facts: dict[str, str] = field(default_factory=dict)

    def add_user(self, message: str) -> None:
        self.history.append(Turn(role="user", content=message))
        self._trim()

    def add_assistant(self, message: str) -> None:
        self.history.append(Turn(role="assistant", content=message))
        self._trim()

    def remember(self, key: str, value: str) -> None:
        self.facts[key] = value

    def recall(self, key: str) -> str | None:
        return self.facts.get(key)

    def context_string(self, max_turns: int = 10) -> str:
        lines: list[str] = []

        if self.facts:
            lines.append("Known facts:")
            for k, v in self.facts.items():
                lines.append(f"  {k}: {v}")
            lines.append("")

        recent = self.history[-max_turns:]
        if recent:
            lines.append("Recent conversation:")
            for t in recent:
                lines.append(f"  {t.role}: {t.content}")

        return "\n".join(lines)

    def _trim(self) -> None:
        if len(self.history) > MAX_HISTORY:
            self.history = self.history[-MAX_HISTORY:]
