from __future__ import annotations

import enum
import logging
import re
from dataclasses import dataclass, field
from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from dan.core.bus import EventBus
    from dan.core.tool_registry import ToolRegistry
    from dan.memory.memory import MemoryManager
    from dan.memory.session import SessionMemory
    from dan.providers.base import Provider
    from dan.skills.skill_registry import SkillRegistry

logger = logging.getLogger(__name__)

_GREETING_RE = re.compile(
    r"^\s*(hola|hello|hi|hey|buenos dias|buenas tardes|buenas noches|que tal|sup|yo|hiya|howdy|greetings|salut|ciao|namaste)\s*[!.??]*\s*$",
    re.IGNORECASE,
)

_GREETING_RESPONSES = {
    "hola": "Hola! En que puedo ayudarte?",
    "hello": "Hello! How can I help you?",
    "hi": "Hi! What can I do for you?",
    "hey": "Hey! What's up?",
    "buenos dias": "Buenos dias! En que puedo ayudarte?",
    "buenas tardes": "Buenas tardes! En que puedo ayudarte?",
    "buenas noches": "Buenas noches! En que puedo ayudarte?",
    "que tal": "Que tal! En que puedo ayudarte?",
}


class Layer(enum.IntEnum):
    REFLEX = 0
    INTERPRET = 1
    REASON = 2
    LEARN = 3


@dataclass
class Route:
    layer: Layer
    tool_name: str | None = None
    confidence: float = 0.0
    args: dict[str, Any] = field(default_factory=dict)
    skill_name: str | None = None
    raw_response: str = ""
    steps: list[dict[str, Any]] = field(default_factory=list)


class Router:
    """Routes user input through intelligence layers.

    L0 (Reflex): Skills + greeting detection. Zero LLM cost.
    L1 (Interpret): Small LLM extracts intent and arguments.
    L2 (Reason): Large LLM for complex multi-step requests.
    L3 (Learn): Compress successful plans into skills.
    """

    def __init__(
        self,
        registry: ToolRegistry,
        skill_registry: SkillRegistry | None = None,
        memory: MemoryManager | None = None,
        bus: EventBus | None = None,
        interpret_provider: Provider | None = None,
        reason_provider: Provider | None = None,
        threshold: float = 1.0,
        session: SessionMemory | None = None,
    ) -> None:
        self.registry = registry
        self.skill_registry = skill_registry
        self.memory = memory
        self.bus = bus
        self.interpret_provider = interpret_provider
        self.reason_provider = reason_provider
        self.threshold = threshold
        self.session = session

    async def route(self, message: str) -> Route:
        # L0: Skills
        if self.skill_registry:
            skill = self.skill_registry.match(message)
            if skill:
                logger.debug("L0 skill match: %s", skill.name)
                return Route(
                    layer=Layer.LEARN,
                    confidence=1.0,
                    skill_name=skill.name,
                    args={"message": message},
                )

        # L0: Greeting fast path — zero LLM cost
        greeting_match = _GREETING_RE.match(message)
        if greeting_match:
            key = greeting_match.group(1).lower()
            response = _GREETING_RESPONSES.get(key, "Hola! En que puedo ayudarte?")
            logger.debug("L0 greeting: %s -> %s", message, response)
            return Route(
                layer=Layer.REFLEX,
                confidence=1.0,
                raw_response=response,
                args={"message": message},
            )

        # L1: Interpret
        if self.interpret_provider and await self.interpret_provider.health_check():
            result = await self._interpret(message)
            if result is not None:
                if result.confidence >= self.threshold:
                    logger.debug("L1 interpret: %s", result.tool_name)
                    return result
                logger.debug("L1 rejected: no tool for '%s'", message)
                return result

        # L2: Reason — only when L1 failed to parse or is unavailable
        if self.reason_provider and await self.reason_provider.health_check():
            route = await self._reason(message)
            if route:
                logger.debug("L2 reason: %s (steps=%d)", route.tool_name or "none", len(route.steps))
                return route

        # No layer
        logger.debug("No layer could handle: %s", message)
        return Route(
            layer=Layer.REFLEX,
            confidence=0.0,
            args={"message": message},
        )

    def _tool_names(self) -> str:
        """Just tool names, one per line — minimal context for L1."""
        return "\n".join(t.name for t in self.registry.tools())

    def _tool_categories(self) -> str:
        """Condensed category list for L2 reason model."""
        from collections import defaultdict

        categories: dict[str, list[str]] = defaultdict(list)
        for t in self.registry.tools():
            cat = t.__module__.rsplit(".", 1)[-1].replace(".py", "")
            categories[cat].append(t.name)

        lines = []
        for cat, names in sorted(categories.items()):
            lines.append(f"  {cat}: {', '.join(names)}")
        return "\n".join(lines)

    def _session_context(self) -> str:
        if self.session:
            return self.session.context_string(max_turns=6)
        return ""

    async def _interpret(self, message: str) -> Route | None:
        if not self.interpret_provider:
            return None

        route = await self._interpret_once(message)
        if route is not None:
            return route

        logger.debug("L1 parse failed, retrying: %s", message)
        return await self._interpret_once(message)

    async def _interpret_once(self, message: str) -> Route | None:
        from dan.providers.base import ProviderMessage

        content = message
        ctx = self._session_context()
        if ctx:
            content = f"{ctx}\n\nUser: {message}"

        messages = [ProviderMessage(role="user", content=content)]

        try:
            response = await self.interpret_provider.complete(
                messages, temperature=0.1, max_tokens=256
            )
            logger.debug("L1 raw response: %r", response.text)
            return self._parse_interpretation(response.text, message)
        except Exception:
            logger.exception("L1 interpretation failed")
            return None

    async def _reason(self, message: str) -> Route | None:
        if not self.reason_provider:
            return None

        from dan.providers.base import ProviderMessage

        content = message
        ctx = self._session_context()
        if ctx:
            content = f"{ctx}\n\nUser: {message}"

        messages = [ProviderMessage(role="user", content=content)]

        try:
            response = await self.reason_provider.complete(
                messages, temperature=0.2, max_tokens=256
            )
            route = self._parse_reasoning(response.text, message)
            if route is not None:
                return route

            text = response.text.strip()
            if text:
                return Route(
                    layer=Layer.REASON,
                    confidence=0.0,
                    raw_response=text,
                    args={"message": message},
                )
            return None
        except Exception:
            logger.exception("L2 reasoning failed")
            return None

    def _parse_interpretation(self, text: str, original: str) -> Route | None:
        data = self._extract_json(text)
        if data is None:
            logger.warning("Failed to parse L1 response: %s", text)
            return None

        tool_name = data.get("tool")
        confidence = float(data.get("confidence", 0))
        args = data.get("args", {})
        args["message"] = original

        if tool_name and tool_name in self.registry:
            if not self._validate_tool_match(tool_name, original):
                logger.debug("L1 tool match rejected: %s", tool_name)
                return Route(
                    layer=Layer.INTERPRET,
                    confidence=0.0,
                    args={"message": original},
                )
            return Route(
                layer=Layer.INTERPRET,
                tool_name=tool_name,
                confidence=confidence,
                args=args,
                raw_response=text,
            )

        return Route(
            layer=Layer.INTERPRET,
            confidence=0.0,
            args={"message": original},
        )

    def _validate_tool_match(self, tool_name: str, message: str) -> bool:
        msg = message.lower().strip()

        if tool_name == "current_time":
            schedule_words = {"close", "opens", "shut", "start", "end", "schedule"}
            has_schedule = any(w in msg for w in schedule_words)
            has_time_query = any(w in msg for w in {"what time", "que hora", "hora es", "hour"})
            if has_schedule and not has_time_query:
                return False

        return True

    def _parse_reasoning(self, text: str, original: str) -> Route | None:
        data = self._extract_json(text)
        if data is None:
            logger.warning("Failed to parse L2 response: %s", text)
            return None

        steps = data.get("steps", [])
        confidence = float(data.get("confidence", 0))

        valid_steps: list[dict[str, Any]] = []
        for step in steps:
            tn = step.get("tool")
            if tn and tn in self.registry:
                step_args = step.get("args", {})
                step_args["message"] = original
                valid_steps.append({"tool": tn, "args": step_args})

        if valid_steps:
            first = valid_steps[0]
            return Route(
                layer=Layer.REASON,
                tool_name=first["tool"],
                confidence=confidence,
                args=first["args"],
                raw_response=text,
                steps=valid_steps,
            )
        return None

    @staticmethod
    def _extract_json(text: str) -> dict | None:
        import json

        text = text.strip()

        # Fix common qwen3 quirk: ) instead of }
        text = re.sub(r'"\s*\)\s*$', '"}', text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            pass

        start = text.find("{")
        if start == -1:
            return None

        depth = 0
        for i in range(start, len(text)):
            if text[i] == "{":
                depth += 1
            elif text[i] in ("}", ")"):
                depth -= 1
                if depth == 0:
                    candidate = text[start : i + 1]
                    # Fix ) -> } at end
                    candidate = candidate.rstrip(")") + "}"
                    try:
                        return json.loads(candidate)
                    except json.JSONDecodeError:
                        return None
        return None
