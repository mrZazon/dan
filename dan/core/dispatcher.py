from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import TYPE_CHECKING

from dan.core.tool_registry import ToolRegistry

if TYPE_CHECKING:
    from dan.core.tool_match import ToolMatch

logger = logging.getLogger(__name__)

DEFAULT_THRESHOLD = 1.0


@dataclass
class DispatchResult:
    """Result of dispatching a message."""

    match: ToolMatch | None
    confidence: float = 0.0
    message: str = ""
    metadata: dict[str, object] = field(default_factory=dict)


class Dispatcher:
    """Entry point for message dispatch.

    Receives user requests, scores them against registered tools,
    and returns the best match if confidence exceeds the threshold.
    """

    def __init__(
        self,
        registry: ToolRegistry | None = None,
        threshold: float = DEFAULT_THRESHOLD,
    ) -> None:
        self.registry = registry or ToolRegistry()
        if not self.registry.names():
            self.registry.discover()
        self.threshold = threshold

    def dispatch(self, message: str) -> DispatchResult:
        """Dispatch a message to find the best matching tool.

        Args:
            message: The user's input message.

        Returns:
            DispatchResult with the best ToolMatch or None.
        """
        match = self.registry.match(message)

        if match is None:
            logger.debug("No tool matched for: %s", message)
            return DispatchResult(match=None, confidence=0.0, message="No matching tool found.")

        if match.score < self.threshold:
            logger.debug(
                "Best match '%s' scored %.1f below threshold %.1f",
                match.tool.name,
                match.score,
                self.threshold,
            )
            return DispatchResult(
                match=None,
                confidence=match.score,
                message=f"Best match '{match.tool.name}' below threshold.",
            )

        logger.debug("Matched tool '%s' with score %.1f", match.tool.name, match.score)
        return DispatchResult(match=match, confidence=match.score, message="Match found.")
