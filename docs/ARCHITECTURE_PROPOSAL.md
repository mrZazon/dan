# D.A.N. Architecture Proposal

## Executive Summary

This document proposes an evolution of the D.A.N. codebase from a simple tool dispatch system into a scalable Agentic Execution Framework with four intelligence layers (L0-L3), service-oriented architecture, plugin system, event bus, memory, and learning pipeline.

**Core Principle**: Evolution, not rewriting. Every proposed change preserves existing working components.

---

## 1. Current Architecture Analysis

### 1.1 What Exists

```
dan/
├── core/
│   ├── dispatcher.py      # Scores messages against tools, returns best match
│   ├── tool_registry.py   # Auto-discovers and registers @tool-decorated classes
│   └── tool_match.py      # ToolMatch dataclass (tool, score)
├── tools/
│   ├── base.py            # Tool ABC + ToolResult dataclass
│   ├── decorators.py      # @tool decorator for auto-discovery
│   ├── command.py         # Shell command executor
│   ├── echo.py            # Echo tool
│   └── hour.py            # Current time tool
└── [empty placeholders]
    ├── config/
    ├── context/
    ├── planner/
    ├── plugins/
    ├── reasoning/
    ├── services/
    └── ...
```

### 1.2 Execution Flow (Current)

```
User Input
    ↓
Dispatcher.dispatch(message)
    ↓
Score each tool against message
    ↓
Return tool name with highest score (or None)
    ↓
ToolRegistry.execute(match)
    ↓
Tool.execute(**kwargs)
    ↓
ToolResult
```

### 1.3 Identified Issues

| Issue | Impact |
|-------|--------|
| Dispatcher returns `str`, not `ToolMatch` | Loses score information |
| Duplicate scoring logic in Tool.score() and Dispatcher | Violates DRY |
| No confidence threshold | Returns tools with score 0 |
| No argument extraction from message | Tools receive empty kwargs |
| Dispatcher is sync, tools are async | Mixing concerns |
| No service layer | Tools directly call OS APIs |
| No plugin system | Only dan.tools package discoverable |
| No configuration management | Hardcoded values |
| No event system | No observability or extensibility |
| No context/memory | Stateless interactions |
| No LLM integration | No interpretation or reasoning |

---

## 2. Strengths to Preserve

| Component | Why Keep |
|-----------|----------|
| `Tool` ABC | Clean abstraction, async execution |
| `ToolResult` | Standardized response format |
| `@tool` decorator | Elegant auto-discovery |
| `ToolRegistry` | Working discovery mechanism |
| Tool pattern (name, description, aliases, intents) | Good intent-matching design |
| `apps/` structure | Clean separation of entry points |

---

## 3. Proposed Folder Structure

```
dan/
├── apps/
│   ├── __init__.py
│   ├── cli/
│   │   ├── __init__.py
│   │   └── main.py              # CLI entry point
│   ├── daemon/
│   │   ├── __init__.py
│   │   └── main.py              # Daemon entry point
│   └── gui/
│       ├── __init__.py
│       └── main.py              # KDE GUI entry point
│
├── dan/
│   ├── __init__.py
│   │
│   ├── core/                    # Core framework
│   │   ├── __init__.py
│   │   ├── bus.py               # Event bus
│   │   ├── config.py            # Configuration manager
│   │   ├── dispatcher.py        # Intent dispatcher (L0)
│   │   ├── registry.py          # Tool registry
│   │   ├── router.py            # Intelligence router (L0-L3)
│   │   ├── tool_match.py        # ToolMatch dataclass
│   │   └── types.py             # Shared types and protocols
│   │
│   ├── engine/                  # Execution engine
│   │   ├── __init__.py
│   │   ├── executor.py          # Task executor
│   │   ├── planner.py           # Multi-step planner (L2)
│   │   └── orchestrator.py      # Tool orchestration
│   │
│   ├── interpret/               # Interpretation layer (L1)
│   │   ├── __init__.py
│   │   ├── interpreter.py       # Message interpreter
│   │   ├── extractor.py         # Argument extractor
│   │   └── intent.py            # Intent classification
│   │
│   ├── memory/                  # Memory system
│   │   ├── __init__.py
│   │   ├── memory.py            # Memory manager
│   │   ├── short_term.py        # Session memory
│   │   ├── long_term.py         # Persistent memory
│   │   └── skills.py            # Learned skills storage
│   │
│   ├── skills/                  # Skill system (L3)
│   │   ├── __init__.py
│   │   ├── skill.py             # Skill base class
│   │   ├── skill_registry.py    # Skill discovery
│   │   └── skill_store.py       # Skill persistence
│   │
│   ├── learn/                   # Learning layer (L3)
│   │   ├── __init__.py
│   │   ├── learner.py           # Pattern detector
│   │   ├── compressor.py        # Plan compressor
│   │   └── trainer.py           # Skill trainer
│   │
│   ├── providers/               # Model providers (Intel-first)
│   │   ├── __init__.py
│   │   ├── base.py              # Provider ABC
│   │   ├── ipex.py              # IPEX-LLM provider (PRIMARY)
│   │   └── openai.py            # OpenAI provider (fallback)
│   │
│   ├── services/                # Business logic
│   │   ├── __init__.py
│   │   ├── base.py              # Service ABC
│   │   ├── shell.py             # Shell service
│   │   ├── audio.py             # Audio service
│   │   ├── power.py             # Power service
│   │   ├── browser.py           # Browser service
│   │   └── system.py            # System service
│   │
│   ├── speech/                  # Voice pipeline
│   │   ├── __init__.py
│   │   ├── stt.py               # Speech-to-text
│   │   ├── tts.py               # Text-to-speech
│   │   └── pipeline.py          # Voice pipeline
│   │
│   ├── tools/                   # Tools (adapters)
│   │   ├── __init__.py
│   │   ├── base.py              # Tool ABC
│   │   ├── decorators.py        # @tool decorator
│   │   ├── command.py           # Shell command tool
│   │   ├── echo.py              # Echo tool
│   │   └── hour.py              # Time tool
│   │
│   ├── plugins/                 # Plugin system
│   │   ├── __init__.py
│   │   ├── manager.py           # Plugin manager
│   │   ├── loader.py            # Plugin loader
│   │   └── base.py              # Plugin ABC
│   │
│   ├── kde/                     # KDE integration
│   │   ├── __init__.py
│   │   ├── notifications.py     # Notification manager
│   │   ├── plasma.py            # Plasma integration
│   │   └── widgets.py           # Widget system
│   │
│   └── context/                 # Context management
│       ├── __init__.py
│       └── context.py           # Context manager
│
├── tests/
│   ├── __init__.py
│   ├── test_core/
│   ├── test_tools/
│   ├── test_interpret/
│   ├── test_memory/
│   └── test_skills/
│
├── docs/
│   ├── ARCHITECTURE.md
│   └── DESIGN_PRINCIPLES.md
│
├── runtime/
│   ├── cache/
│   ├── logs/
│   ├── models/
│   ├── sessions/
│   └── tmp/
│
├── assets/
│
├── pyproject.toml
├── README.md
├── LICENSE
└── .gitignore
```

---

## 4. Package Organization

### 4.1 Core Package (`dan.core`)

**Purpose**: Framework backbone - event bus, configuration, registry, routing.

```
dan.core
├── types.py           # Shared protocols, TypeAliases, enums
├── config.py          # Configuration manager (YAML/TOML based)
├── bus.py             # Event bus (pub/sub)
├── registry.py        # Tool registry (refactored from tool_registry.py)
├── dispatcher.py      # L0 intent dispatcher (refactored)
├── router.py          # Intelligence router (L0 → L1 → L2 → L3)
└── tool_match.py      # ToolMatch dataclass (preserved)
```

### 4.2 Engine Package (`dan.engine`)

**Purpose**: Execution orchestration - planners, executors, orchestrators.

```
dan.engine
├── executor.py        # Single task executor
├── planner.py         # Multi-step planner (L2 reasoning)
└── orchestrator.py    # Parallel tool execution
```

### 4.3 Interpret Package (`dan.interpret`)

**Purpose**: L1 interpretation - extract structured data from natural language.

```
dan.interpret
├── interpreter.py     # Main interpreter (uses L1 model)
├── extractor.py       # Extract arguments from text
└── intent.py          # Intent classification
```

### 4.4 Memory Package (`dan.memory`)

**Purpose**: Memory management - short-term, long-term, skills.

```
dan.memory
├── memory.py          # Memory manager (facade)
├── short_term.py      # Session-scoped memory
├── long_term.py       # Persistent memory (SQLite/JSON)
└── skills.py          # Learned skill storage
```

### 4.5 Skills Package (`dan.skills`)

**Purpose**: Skill system - compressed workflows that bypass reasoning.

```
dan.skills
├── skill.py           # Skill base class
├── skill_registry.py  # Skill discovery
└── skill_store.py     # Skill persistence
```

### 4.6 Learn Package (`dan.learn`)

**Purpose**: L3 learning - detect patterns, compress plans into skills.

```
dan.learn
├── learner.py         # Pattern detector
├── compressor.py      # Plan → Skill compressor
└── trainer.py         # Skill trainer
```

### 4.7 Providers Package (`dan.providers`)

**Purpose**: Model provider abstraction - Intel-first, never depend on specific LLM.

```
dan.providers
├── base.py            # Provider ABC
├── ipex.py            # IPEX-LLM provider (PRIMARY - Intel hardware)
└── openai.py          # OpenAI provider (fallback for non-Intel)
```

### 4.8 Services Package (`dan.services`)

**Purpose**: Business logic - all OS/system interactions.

```
dan.services
├── base.py            # Service ABC
├── shell.py           # Shell command service
├── audio.py           # Audio/volume service
├── power.py           # Battery/power service
├── browser.py         # Browser control service
└── system.py          # System information service
```

### 4.9 Tools Package (`dan.tools`)

**Purpose**: Tool adapters - thin wrappers that delegate to services.

```
dan.tools
├── base.py            # Tool ABC (preserved)
├── decorators.py      # @tool decorator (preserved)
├── command.py         # CommandTool → ShellService
├── echo.py            # EchoTool (preserved)
└── hour.py            # HourTool (preserved)
```

### 4.10 Plugins Package (`dan.plugins`)

**Purpose**: Plugin system - discover and load external extensions.

```
dan.plugins
├── manager.py         # Plugin lifecycle manager
├── loader.py          # Dynamic module loader
└── base.py            # Plugin ABC
```

---

## 5. Dependency Graph

```
                    ┌─────────────┐
                    │   apps/     │
                    │ cli, daemon │
                    │    gui      │
                    └──────┬──────┘
                           │
                    ┌──────▼──────┐
                    │  dan.core   │
                    │  router,    │
                    │  bus, config│
                    └──────┬──────┘
                           │
          ┌────────────────┼────────────────┐
          │                │                │
   ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
   │  dan.engine │ │ dan.interpret│ │  dan.memory │
   │  executor,  │ │ interpreter,│ │  memory,    │
   │  planner    │ │ extractor   │ │  skills     │
   └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
          │                │                │
          └────────────────┼────────────────┘
                           │
                    ┌──────▼──────┐
                    │  dan.skills │
                    │  skill,     │
                    │  registry   │
                    └──────┬──────┘
                           │
           ┌────────────────┼────────────────┐
           │                │                │
    ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
    │  dan.learn  │ │dan.providers│ │  dan.tools  │
    │  learner,   │ │  base,      │ │  base,      │
    │  compressor │ │  ipex,      │ │  command,   │
    └─────────────┘ └─────────────┘ │  echo, hour │
                                   └──────┬──────┘
                                          │
                                   ┌──────▼──────┐
                                   │dan.services │
                                   │  shell,     │
                                   │  audio,     │
                                   │  power      │
                                   └─────────────┘
```

---

## 6. Interface Definitions

### 6.1 Tool Interface (Preserved)

```python
# dan/tools/base.py - PRESERVED

from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any

@dataclass(slots=True)
class ToolResult:
    success: bool
    message: str = ""
    data: Any = None
    metadata: dict[str, Any] = field(default_factory=dict)

class Tool(ABC):
    name: str = ""
    description: str = ""
    aliases: tuple[str, ...] = ()
    intents: dict[str, float] = {}

    @abstractmethod
    async def execute(self, **kwargs: Any) -> ToolResult:
        raise NotImplementedError
```

### 6.2 Provider Interface

```python
# dan/providers/base.py

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

@dataclass
class ProviderResponse:
    text: str
    model: str
    usage: dict[str, int]
    metadata: dict[str, Any]

class Provider(ABC):
    """Model-agnostic provider interface.
    
    Intel-first: IPEX-LLM is the primary provider.
    Models are interchangeable behind this stable interface.
    """

    name: str = ""
    model: str = ""

    @abstractmethod
    async def complete(
        self,
        messages: list[dict[str, str]],
        temperature: float = 0.7,
        max_tokens: int = 1024,
        **kwargs: Any,
    ) -> ProviderResponse:
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError

    @abstractmethod
    async def load_model(self, model_name: str) -> None:
        """Load a model into memory."""
        raise NotImplementedError

    @abstractmethod
    async def unload_model(self) -> None:
        """Unload model from memory."""
        raise NotImplementedError
```

### 6.3 Service Interface

```python
# dan/services/base.py

from abc import ABC, abstractmethod
from typing import Any

class Service(ABC):
    """Base class for all services."""

    name: str = ""

    @abstractmethod
    async def initialize(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def shutdown(self) -> None:
        raise NotImplementedError

    @abstractmethod
    async def health_check(self) -> bool:
        raise NotImplementedError
```

### 6.4 Skill Interface

```python
# dan/skills/skill.py

from dataclasses import dataclass, field
from typing import Any
from dan.tools.base import Tool, ToolResult

@dataclass
class SkillStep:
    tool_name: str
    args: dict[str, Any]
    conditions: dict[str, Any] = field(default_factory=dict)

class Skill:
    """A compressed workflow that bypasses reasoning."""

    name: str = ""
    description: str = ""
    steps: list[SkillStep] = field(default_factory=list)
    triggers: list[str] = field(default_factory=list)
    confidence: float = 0.0

    async def execute(self, context: dict[str, Any]) -> ToolResult:
        """Execute the skill steps sequentially."""
        raise NotImplementedError
```

### 6.5 Event Bus Interface

```python
# dan/core/bus.py

from abc import ABC, abstractmethod
from typing import Any, Callable, Awaitable

EventHandler = Callable[..., Awaitable[None]]

class EventBus:
    """Pub/sub event system."""

    @abstractmethod
    def subscribe(self, event: str, handler: EventHandler) -> None:
        raise NotImplementedError

    @abstractmethod
    def unsubscribe(self, event: str, handler: EventHandler) -> None:
        raise NotImplementedError

    @abstractmethod
    async def publish(self, event: str, **data: Any) -> None:
        raise NotImplementedError
```

### 6.6 Plugin Interface

```python
# dan/plugins/base.py

from abc import ABC, abstractmethod

class Plugin(ABC):
    """Base class for all plugins."""

    name: str = ""
    version: str = ""
    description: str = ""

    @abstractmethod
    async def activate(self, context: dict) -> None:
        raise NotImplementedError

    @abstractmethod
    async def deactivate(self) -> None:
        raise NotImplementedError
```

---

## 7. Router Architecture (L0-L3)

```
                        User Input
                            │
                    ┌───────▼───────┐
                    │     Router     │
                    │  (orchestrator)│
                    └───────┬───────┘
                            │
            ┌───────────────┼───────────────┐
            │               │               │
     ┌──────▼──────┐ ┌──────▼──────┐ ┌──────▼──────┐
     │  L0: Reflex │ │ L1: Interpret│ │ L2: Reason  │
     │  (instant)  │ │  (fast)     │ │  (complex)  │
     └──────┬──────┘ └──────┬──────┘ └──────┬──────┘
            │               │               │
            │          ┌────▼────┐     ┌────▼────┐
            │          │  LLM    │     │  LLM    │
            │          │ (small) │     │ (large) │
            │          └─────────┘     └─────────┘
            │
     ┌──────▼──────┐
     │ L3: Learning │
     │ (compress)   │
     └─────────────┘
```

### 7.1 Router Implementation

```python
# dan/core/router.py

from enum import Enum
from dataclasses import dataclass
from typing import Any

class IntelligenceLayer(Enum):
    REFLEX = 0      # Deterministic, no LLM
    INTERPRET = 1   # Small LLM
    REASON = 2      # Large LLM
    LEARN = 3       # Compressed skills

@dataclass
class RoutingDecision:
    layer: IntelligenceLayer
    tool_name: str | None
    confidence: float
    args: dict[str, Any]
    skill: Any | None = None

class Router:
    """
    Routes user input through intelligence layers.
    
    L0 (Reflex): Check if message matches a skill or tool directly.
    L1 (Interpret): Use small LLM to extract intent and arguments.
    L2 (Reason): Use large LLM for multi-step planning.
    L3 (Learn): Compress successful plans into skills.
    """

    def __init__(
        self,
        registry,
        skill_registry,
        provider_small,
        provider_large,
        memory,
        threshold: float = 0.5,
    ):
        self.registry = registry
        self.skill_registry = skill_registry
        self.provider_small = provider_small
        self.provider_large = provider_large
        self.memory = memory
        self.threshold = threshold

    async def route(self, message: str) -> RoutingDecision:
        # L0: Check skills first
        skill = await self._check_skills(message)
        if skill:
            return RoutingDecision(
                layer=IntelligenceLayer.LEARN,
                tool_name=None,
                confidence=1.0,
                args={"message": message},
                skill=skill,
            )

        # L0: Check tools directly
        decision = await self._check_tools(message)
        if decision and decision.confidence >= self.threshold:
            return decision

        # L1: Interpret with small model
        decision = await self._interpret(message)
        if decision and decision.confidence >= self.threshold:
            return decision

        # L2: Reason with large model
        return await self._reason(message)
```

---

## 8. Execution Flow (Proposed)

### 8.1 Simple Request (L0)

```
User: "What time is it?"
    ↓
Router.route(message)
    ↓
L0: Check tools → HourTool matches (score: 15.0)
    ↓
Confidence >= threshold → Execute directly
    ↓
HourTool.execute() → ToolResult(success=True, message="Current time is: 14:30:00")
```

### 8.2 Complex Request (L1)

```
User: "Turn up the volume"
    ↓
Router.route(message)
    ↓
L0: No direct match (score: 0)
    ↓
L1: Interpreter with small LLM
    ↓
Extracted: {intent: "volume_up", args: {}}
    ↓
Match to VolumeTool → Execute
    ↓
VolumeTool.execute() → ToolResult(success=True, message="Volume increased")
```

### 8.3 Multi-Step Request (L2)

```
User: "Download the latest kernel source and compile it"
    ↓
Router.route(message)
    ↓
L0: No match
    ↓
L1: Partial match (command tool)
    ↓
L2: Planner with large LLM
    ↓
Plan:
    1. CommandTool: wget https://kernel.org/...
    2. CommandTool: tar xf linux-*.tar.xz
    3. CommandTool: cd linux-* && make -j$(nproc)
    ↓
Orchestrator executes sequentially
    ↓
Result aggregated
```

### 8.4 Learning Flow (L3)

```
User: "What time is it?" (10th time)
    ↓
Router.route(message)
    ↓
L0: HourTool matches
    ↓
Learner observes: same pattern, same tool, same args
    ↓
Compressor creates Skill:
    name: "tell_time"
    triggers: ["what time", "current time", ...]
    steps: [SkillStep(tool="hour", args={})]
    ↓
Future: Router matches skill directly (bypass reasoning)
```

---

## 9. Event System

### 9.1 Events

```python
# Event types
class Events:
    # Tool events
    TOOL_REGISTERED = "tool.registered"
    TOOL_EXECUTED = "tool.executed"
    TOOL_FAILED = "tool.failed"

    # Router events
    ROUTE_STARTED = "route.started"
    ROUTE_COMPLETED = "route.completed"
    ROUTE_FAILED = "route.failed"

    # Skill events
    SKILL_CREATED = "skill.created"
    SKILL_EXECUTED = "skill.executed"

    # Provider events
    PROVIDER_REQUEST = "provider.request"
    PROVIDER_RESPONSE = "provider.response"
    PROVIDER_ERROR = "provider.error"

    # System events
    SYSTEM_STARTUP = "system.startup"
    SYSTEM_SHUTDOWN = "system.shutdown"
```

### 9.2 Event Bus Implementation

```python
# dan/core/bus.py

import asyncio
from collections import defaultdict
from typing import Any, Callable, Awaitable

EventHandler = Callable[..., Awaitable[None]]

class EventBus:
    def __init__(self):
        self._handlers: dict[str, list[EventHandler]] = defaultdict(list)

    def subscribe(self, event: str, handler: EventHandler) -> None:
        self._handlers[event].append(handler)

    def unsubscribe(self, event: str, handler: EventHandler) -> None:
        self._handlers[event].remove(handler)

    async def publish(self, event: str, **data: Any) -> None:
        for handler in self._handlers.get(event, []):
            await handler(**data)
```

---

## 10. Memory Architecture

### 10.1 Memory Types

```
┌─────────────────────────────────────────────────┐
│                   Memory Manager                │
├─────────────────┬───────────────┬───────────────┤
│   Short-Term    │   Long-Term   │    Skills     │
│   (Session)     │   (Persistent)│   (Learned)   │
├─────────────────┼───────────────┼───────────────┤
│ • Conversation  │ • User prefs  │ • Compressed  │
│   history       │ • Past tasks  │   workflows   │
│ • Current       │ • System      │ • Trigger     │
│   context       │   knowledge   │   patterns    │
│ • Active        │ • learned     │ • Success     │
│   tasks         │   patterns    │   rates       │
└─────────────────┴───────────────┴───────────────┘
```

### 10.2 Memory Interface

```python
# dan/memory/memory.py

from abc import ABC, abstractmethod
from typing import Any

class Memory(ABC):
    @abstractmethod
    async def store(self, key: str, value: Any) -> None:
        raise NotImplementedError

    @abstractmethod
    async def retrieve(self, key: str) -> Any | None:
        raise NotImplementedError

    @abstractmethod
    async def search(self, query: str, limit: int = 10) -> list[Any]:
        raise NotImplementedError

    @abstractmethod
    async def clear(self) -> None:
        raise NotImplementedError
```

---

## 11. Skill Architecture

### 11.1 Skill Lifecycle

```
1. OBSERVATION
   User performs similar action multiple times
       ↓
2. DETECTION
   Learner detects pattern (same intent, same tools, same args)
       ↓
3. COMPRESSION
   Compressor creates Skill from observed plan
       ↓
4. STORAGE
   Skill stored in SkillStore (JSON/SQLite)
       ↓
5. ACTIVATION
   Skill registered in SkillRegistry
       ↓
6. EXECUTION
   Router matches skill → Execute directly (bypass LLM)
```

### 11.2 Skill Format

```json
{
  "name": "tell_time",
  "description": "Tells the current time",
  "triggers": ["what time", "current time", "time now"],
  "steps": [
    {
      "tool": "hour",
      "args": {}
    }
  ],
  "confidence": 0.95,
  "created_at": "2026-07-13T10:00:00",
  "executions": 15,
  "success_rate": 1.0
}
```

---

## 12. Provider Abstraction

### 12.1 Provider Registry

```python
# dan/providers/__init__.py

class ProviderRegistry:
    """Manages model providers.
    
    Intel-first: IPEX-LLM is the default provider.
    """

    def __init__(self):
        self._providers: dict[str, Provider] = {}
        self._default: str = "ipex"  # Intel-first default

    def register(self, provider: Provider) -> None:
        self._providers[provider.name] = provider

    def get(self, name: str | None = None) -> Provider:
        """Get provider by name, or default (IPEX-LLM)."""
        if name is None:
            name = self._default
        return self._providers[name]

    def set_default(self, name: str) -> None:
        """Set default provider."""
        if name not in self._providers:
            raise ValueError(f"Provider '{name}' not registered")
        self._default = name

    def list(self) -> list[str]:
        return list(self._providers.keys())
```

### 12.2 Provider Selection (Intel-First)

```yaml
# Configuration - Intel-first defaults
providers:
  default: "ipex"

interpret:
  provider: "ipex"  # IPEX-LLM for L1 interpretation
  model: "Qwen/Qwen2-0.5B"  # Small model for fast inference

reason:
  provider: "ipex"  # IPEX-LLM for L2 reasoning
  model: "meta-llama/Llama-3.1-8B"  # Larger model for complex tasks
```

### 12.3 IPEX-LLM Integration

IPEX-LLM provides optimized inference on Intel hardware:
- **CPU**: Optimized for Intel CPUs with AVX-512
- **GPU**: Intel Arc, Intel Data Center GPU support
- **Memory**: Efficient quantization (INT4/INT8)
- **Backend**: PyTorch + Intel Extension

```python
# dan/providers/ipex.py

from ipex_llm.transformers import AutoModelForCausalLM, AutoTokenizer

class IPEXProvider(Provider):
    """Intel IPEX-LLM provider - PRIMARY for D.A.N."""
    
    name = "ipex"
    
    def __init__(self):
        self.model = None
        self.tokenizer = None
        self._device = "cpu"  # or "xpu" for Intel GPU
    
    async def load_model(self, model_name: str) -> None:
        """Load model with IPEX-LLM optimization."""
        self.tokenizer = AutoTokenizer.from_pretrained(model_name)
        self.model = AutoModelForCausalLM.from_pretrained(
            model_name,
            load_in_low_bit="nf4",  # INT4 quantization
            device=self._device
        )
    
    async def complete(self, messages, temperature=0.7, max_tokens=1024, **kwargs):
        """Generate completion using IPEX-LLM."""
        # Implementation using IPEX-LLM
        pass
```

### 12.4 IPEX-LLM Installation

**Prerequisites**:
- Python 3.10+
- Intel CPU (AVX-512 support recommended)
- Optional: Intel Arc GPU for accelerated inference

**Installation**:

```bash
# Create virtual environment
python -m venv .venv
source .venv/bin/activate

# Install IPEX-LLM
pip install ipex-llm

# For Intel GPU support (optional)
pip install ipex-llm[xpu]

# Install D.A.N. dependencies
pip install -e .
```

**Model Download** (first run):
```bash
# Models are downloaded automatically on first use
# Default models:
# - L1: Qwen/Qwen2-0.5B (small, fast)
# - L2: meta-llama/Llama-3.1-8B (large, capable)

# Or pre-download:
python -c "from transformers import AutoModelForCausalLM; AutoModelForCausalLM.from_pretrained('Qwen/Qwen2-0.5B')"
```

**Configuration** (`~/.config/dan/config.yaml`):
```yaml
ipex:
  quantization: "nf4"  # INT4 for efficiency
  device: "cpu"        # "cpu" or "xpu" (Intel GPU)
  threads: 4           # CPU threads
  cache_dir: "~/.cache/dan/models"
```

---

## 13. Plugin Architecture

### 13.1 Plugin Discovery

```
1. Scan plugin directories:
   - ~/.local/share/dan/plugins/
   - /usr/share/dan/plugins/
   - ./plugins/ (project-local)

2. Each plugin is a Python package with:
   - plugin.toml (metadata)
   - __init__.py (entry point)

3. Plugin registers:
   - Tools
   - Services
   - Providers
   - Event handlers
```

### 13.2 Plugin Format

```toml
# plugin.toml
[plugin]
name = "my_plugin"
version = "1.0.0"
description = "My custom plugin"
author = "Author Name"

[plugin.entry]
module = "my_plugin"
class = "MyPlugin"
```

---

## 14. Configuration Manager

### 14.1 Configuration Structure

```yaml
# ~/.config/dan/config.yaml

core:
  threshold: 0.5
  log_level: "INFO"

providers:
  default: "ipex"  # Intel-first

interpret:
  provider: "ipex"  # IPEX-LLM for L1
  model: "Qwen/Qwen2-0.5B"
  device: "cpu"  # or "xpu" for Intel GPU

reason:
  provider: "ipex"  # IPEX-LLM for L2
  model: "meta-llama/Llama-3.1-8B"
  device: "cpu"

memory:
  short_term_limit: 100
  long_term_path: "~/.local/share/dan/memory"

skills:
  store_path: "~/.local/share/dan/skills"
  min_executions: 5
  min_confidence: 0.8

plugins:
  directories:
    - "~/.local/share/dan/plugins"

# IPEX-LLM specific settings
ipex:
  quantization: "nf4"  # INT4 quantization for efficiency
  device: "cpu"  # "cpu" or "xpu" (Intel GPU)
  threads: 4  # CPU threads
```

---

## 15. Migration Plan

### Phase 1: Core Refactoring (Week 1)

**Goal**: Fix existing issues, establish clean interfaces.

1. Fix `Dispatcher` to return `ToolMatch` instead of `str`
2. Remove duplicate scoring logic (keep in Tool, remove from Dispatcher)
3. Add confidence threshold to Dispatcher
4. Create `dan/core/types.py` with shared protocols
5. Create `dan/core/bus.py` with Event Bus
6. Create `dan/core/config.py` with Configuration Manager
7. Update `pyproject.toml` with dependencies

**Files to modify**:
- `dan/core/dispatcher.py` → Return ToolMatch, add threshold
- `dan/core/tool_registry.py` → Use Tool.score() instead of duplicate logic
- `dan/tools/base.py` → Preserve as-is

**Files to create**:
- `dan/core/types.py`
- `dan/core/bus.py`
- `dan/core/config.py`

### Phase 2: Service Layer (Week 2)

**Goal**: Extract business logic from tools into services.

1. Create `dan/services/base.py` with Service ABC
2. Create `dan/services/shell.py` (extract from CommandTool)
3. Refactor `CommandTool` to use `ShellService`
4. Create other services (audio, power, browser, system)

**Files to create**:
- `dan/services/__init__.py`
- `dan/services/base.py`
- `dan/services/shell.py`
- `dan/services/audio.py`
- `dan/services/power.py`
- `dan/services/browser.py`
- `dan/services/system.py`

**Files to modify**:
- `dan/tools/command.py` → Use ShellService

### Phase 3: Provider Abstraction (Week 3)

**Goal**: Model-agnostic LLM integration with Intel-first approach.

1. Create `dan/providers/base.py` with Provider ABC
2. Create `dan/providers/ipex.py` (IPEX-LLM - PRIMARY)
3. Create `dan/providers/openai.py` (fallback for non-Intel)
4. Create provider registry with Intel-first defaults
5. Update configuration to support provider selection
6. Add IPEX-LLM installation and setup documentation

**Files to create**:
- `dan/providers/__init__.py`
- `dan/providers/base.py`
- `dan/providers/ipex.py` (PRIMARY)
- `dan/providers/openai.py` (fallback)

### Phase 4: Interpretation Layer (Week 4)

**Goal**: L1 interpretation with small LLM.

1. Create `dan/interpret/interpreter.py`
2. Create `dan/interpret/extractor.py`
3. Create `dan/interpret/intent.py`
4. Integrate with Router

**Files to create**:
- `dan/interpret/__init__.py`
- `dan/interpret/interpreter.py`
- `dan/interpret/extractor.py`
- `dan/interpret/intent.py`

### Phase 5: Router (Week 5)

**Goal**: Intelligence routing L0-L3.

1. Create `dan/core/router.py`
2. Integrate Dispatcher, Interpreter, Planner
3. Add skill checking
4. Add learning hooks

**Files to create**:
- `dan/core/router.py`

### Phase 6: Memory (Week 6)

**Goal**: Memory system.

1. Create `dan/memory/memory.py`
2. Create `dan/memory/short_term.py`
3. Create `dan/memory/long_term.py`
4. Integrate with Router

**Files to create**:
- `dan/memory/__init__.py`
- `dan/memory/memory.py`
- `dan/memory/short_term.py`
- `dan/memory/long_term.py`

### Phase 7: Skills (Week 7)

**Goal**: Skill system.

1. Create `dan/skills/skill.py`
2. Create `dan/skills/skill_registry.py`
3. Create `dan/skills/skill_store.py`
4. Integrate with Router

**Files to create**:
- `dan/skills/__init__.py`
- `dan/skills/skill.py`
- `dan/skills/skill_registry.py`
- `dan/skills/skill_store.py`

### Phase 8: Learning (Week 8)

**Goal**: Learning pipeline.

1. Create `dan/learn/learner.py`
2. Create `dan/learn/compressor.py`
3. Create `dan/learn/trainer.py`
4. Integrate with Router and Memory

**Files to create**:
- `dan/learn/__init__.py`
- `dan/learn/learner.py`
- `dan/learn/compressor.py`
- `dan/learn/trainer.py`

### Phase 9: Engine (Week 9)

**Goal**: Execution engine.

1. Create `dan/engine/executor.py`
2. Create `dan/engine/planner.py`
3. Create `dan/engine/orchestrator.py`
4. Integrate with Router

**Files to create**:
- `dan/engine/__init__.py`
- `dan/engine/executor.py`
- `dan/engine/planner.py`
- `dan/engine/orchestrator.py`

### Phase 10: Plugin System (Week 10)

**Goal**: Plugin architecture.

1. Create `dan/plugins/base.py`
2. Create `dan/plugins/manager.py`
3. Create `dan/plugins/loader.py`
4. Integrate with Registry

**Files to create**:
- `dan/plugins/__init__.py`
- `dan/plugins/base.py`
- `dan/plugins/manager.py`
- `dan/plugins/loader.py`

### Phase 11: Voice Pipeline (Week 11)

**Goal**: Speech integration.

1. Create `dan/speech/stt.py`
2. Create `dan/speech/tts.py`
3. Create `dan/speech/pipeline.py`

**Files to create**:
- `dan/speech/__init__.py`
- `dan/speech/stt.py`
- `dan/speech/tts.py`
- `dan/speech/pipeline.py`

### Phase 12: KDE Integration (Week 12)

**Goal**: Desktop integration.

1. Create `dan/kde/notifications.py`
2. Create `dan/kde/plasma.py`
3. Create `dan/kde/widgets.py`

**Files to create**:
- `dan/kde/__init__.py`
- `dan/kde/notifications.py`
- `dan/kde/plasma.py`
- `dan/kde/widgets.py`

---

## 16. Component Preservation Summary

### Preserved As-Is
- `dan/tools/base.py` → Tool ABC, ToolResult
- `dan/tools/decorators.py` → @tool decorator
- `dan/tools/echo.py` → EchoTool
- `dan/tools/hour.py` → HourTool
- `dan/core/tool_match.py` → ToolMatch dataclass

### Refactored
- `dan/core/dispatcher.py` → Returns ToolMatch, adds threshold
- `dan/core/tool_registry.py` → Cleaner discovery, uses Tool.score()
- `dan/tools/command.py` → Uses ShellService

### New Components
- `dan/core/bus.py` → Event bus
- `dan/core/config.py` → Configuration manager
- `dan/core/router.py` → Intelligence router
- `dan/core/types.py` → Shared protocols
- `dan/engine/*` → Execution engine
- `dan/interpret/*` → Interpretation layer
- `dan/memory/*` → Memory system
- `dan/skills/*` → Skill system
- `dan/learn/*` → Learning pipeline
- `dan/providers/ipex.py` → IPEX-LLM provider (PRIMARY)
- `dan/providers/openai.py` → OpenAI provider (fallback)
- `dan/services/*` → Business logic
- `dan/plugins/*` → Plugin system
- `dan/speech/*` → Voice pipeline
- `dan/kde/*` → KDE integration

---

## 17. ASCII Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                              D.A.N. Architecture                            │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                             │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────┐                         │
│  │     CLI     │  │   Daemon    │  │     GUI     │    Apps Layer           │
│  └──────┬──────┘  └──────┬──────┘  └──────┬──────┘                         │
│         │                │                │                                 │
│         └────────────────┼────────────────┘                                 │
│                          │                                                  │
│                   ┌──────▼──────┐                                           │
│                   │    Router    │    Intelligence Router                   │
│                   │   (L0-L3)   │                                           │
│                   └──────┬──────┘                                           │
│                          │                                                  │
│    ┌─────────────────────┼─────────────────────┐                           │
│    │                     │                     │                            │
│    ▼                     ▼                     ▼                            │
│ ┌──────────┐      ┌──────────┐          ┌──────────┐                       │
│ │  L0:     │      │  L1:     │          │  L2:     │   Intelligence Layers│
│ │  Reflex  │      │  Interpret│         │  Reason  │                       │
│ │  (Tools) │      │  (Small  │          │  (Large  │                       │
│ │          │      │   LLM)   │          │   LLM)   │                       │
│ └────┬─────┘      └────┬─────┘          └────┬─────┘                       │
│      │                 │                     │                              │
│      │           ┌─────▼─────┐         ┌─────▼─────┐                       │
│      │           │ Providers │         │  Engine   │                       │
│      │           │ IPEX-LLM  │         │ Executor, │                       │
│      │           │ (primary),│         │ Planner,  │                       │
│      │           │ OpenAI    │         │ Orchestr. │                       │
│      │           └───────────┘         └───────────┘                       │
│      │                                                                     │
│      │    ┌─────────────────────────────────────────────┐                  │
│      │    │              Memory System                  │                  │
│      │    │  ┌───────────┐ ┌───────────┐ ┌───────────┐  │                  │
│      │    │  │ Short-Term│ │ Long-Term │ │  Skills   │  │                  │
│      │    │  └───────────┘ └───────────┘ └───────────┘  │                  │
│      │    └─────────────────────────────────────────────┘                  │
│      │                                                                     │
│      │    ┌─────────────────────────────────────────────┐                  │
│      │    │              Learning Layer                 │                  │
│      │    │  ┌───────────┐ ┌───────────┐ ┌───────────┐  │                  │
│      │    │  │  Learner  │ │Compressor │ │  Trainer  │  │                  │
│      │    │  └───────────┘ └───────────┘ └───────────┘  │                  │
│      │    └─────────────────────────────────────────────┘                  │
│      │                                                                     │
│      ▼                                                                     │
│ ┌──────────────────────────────────────────────────────────────────────┐   │
│ │                         Tool Layer                                   │   │
│ │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│ │  │ Command  │ │   Echo   │ │   Hour   │ │ Browser  │ │  Volume  │  │   │
│ │  │  Tool    │ │   Tool   │ │   Tool   │ │   Tool   │ │   Tool   │  │   │
│ │  └────┬─────┘ └──────────┘ └──────────┘ └────┬─────┘ └────┬─────┘  │   │
│ │       │                                       │            │         │   │
│ └───────┼───────────────────────────────────────┼────────────┼─────────┘   │
│         │                                       │            │             │
│         ▼                                       ▼            ▼             │
│ ┌──────────────────────────────────────────────────────────────────────┐   │
│ │                       Service Layer                                  │   │
│ │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│ │  │  Shell   │ │  Audio   │ │  Power   │ │ Browser  │ │  System  │  │   │
│ │  │ Service  │ │ Service  │ │ Service  │ │ Service  │ │ Service  │  │   │
│ │  └────┬─────┘ └────┬─────┘ └────┬─────┘ └──────────┘ └──────────┘  │   │
│ └───────┼────────────┼────────────┼────────────────────────────────────┘   │
│         │            │            │                                        │
│         ▼            ▼            ▼                                        │
│ ┌──────────────────────────────────────────────────────────────────────┐   │
│ │                        Linux System                                  │   │
│ │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│ │  │  Shell   │ │ PipeWire │ │  UPower  │ │ Browser  │ │  /proc   │  │   │
│ │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│ └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
│  ┌──────────────────────────────────────────────────────────────────────┐   │
│  │                     Cross-Cutting Concerns                           │   │
│  │  ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐ ┌──────────┐  │   │
│  │  │ Event    │ │   Config │ │  Plugin  │ │  Speech  │ │   KDE    │  │   │
│  │  │   Bus    │ │  Manager │ │ Manager  │ │ Pipeline │ │Integration│  │   │
│  │  └──────────┘ └──────────┘ └──────────┘ └──────────┘ └──────────┘  │   │
│  └──────────────────────────────────────────────────────────────────────┘   │
│                                                                             │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 18. Key Design Decisions

### 18.1 Why Composition Over Inheritance

Tools compose with Services, not inherit from them:
```python
class CommandTool(Tool):
    def __init__(self, shell_service: ShellService):
        self.shell = shell_service

    async def execute(self, **kwargs):
        return await self.shell.execute(kwargs["command"])
```

### 18.2 Why Model Agnostic (Intel-First)

Providers implement a common interface, with IPEX-LLM as primary:
```python
# Never do this:
from ollama import chat

# Always do this:
provider = registry.get()  # Returns IPEX-LLM by default
response = await provider.complete(messages)

# Or explicitly:
provider = registry.get("ipex")  # Intel hardware
provider = registry.get("openai")  # Fallback for non-Intel
```

### 18.3 Why Event-Driven

The Event Bus enables loose coupling:
```python
# Tool emits event
await bus.publish("tool.executed", tool="hour", result=result)

# Logger listens
bus.subscribe("tool.executed", log_tool_execution)

# Metrics collector listens
bus.subscribe("tool.executed", collect_metrics)
```

### 18.4 Why Skills Over Rules

Skills are learned, not hard-coded:
```python
# Instead of:
if "time" in message:
    return HourTool()

# Skills are:
skill = Skill(
    name="tell_time",
    triggers=["what time", "current time"],
    steps=[SkillStep(tool="hour", args={})]
)
```

---

## 19. Success Metrics

1. **Existing tools continue to work** without modification (except CommandTool)
2. **New tools can be added** by creating a single file
3. **Plugins can extend** the system without modifying core code
4. **LLM providers can be swapped** without changing business logic
5. **Skills are learned** from repeated patterns
6. **Memory persists** across sessions
7. **Events enable** observability and extensibility

---

## 20. Next Steps

1. **Immediate**: Fix Dispatcher to return ToolMatch
2. **This week**: Add Event Bus and Configuration Manager
3. **Next week**: Create Service Layer
4. **Following weeks**: Implement remaining phases per migration plan

---

*Document generated for D.A.N. Architecture Evolution*
*Preserving working components while enabling scalable growth*
