from __future__ import annotations

import logging
from dataclasses import dataclass, field, fields
from pathlib import Path
from typing import Any

import yaml

logger = logging.getLogger(__name__)

DEFAULT_CONFIG_DIR = Path.home() / ".config" / "dan"
DEFAULT_CONFIG_FILE = DEFAULT_CONFIG_DIR / "config.yaml"
DEFAULT_DATA_DIR = Path.home() / ".local" / "share" / "dan"


def _filter_fields(cls: type, data: dict[str, Any]) -> dict[str, Any]:
    """Filter dict to only keys that are fields of the dataclass."""
    field_names = {f.name for f in fields(cls)}
    return {k: v for k, v in data.items() if k in field_names}


@dataclass
class ProviderConfig:
    """Configuration for a model provider."""

    name: str = "ollama"
    model: str = "qwen3.5:2b"
    device: str = "cpu"
    quantization: str = "nf4"
    max_tokens: int = 1024
    temperature: float = 0.7


@dataclass
class CoreConfig:
    """Core framework configuration."""

    threshold: float = 0.7
    log_level: str = "INFO"


@dataclass
class MemoryConfig:
    """Memory system configuration."""

    short_term_limit: int = 100
    long_term_path: str = str(DEFAULT_DATA_DIR / "memory")


@dataclass
class SkillsConfig:
    """Skill system configuration."""

    store_path: str = str(DEFAULT_DATA_DIR / "skills")
    min_executions: int = 5
    min_confidence: float = 0.8


@dataclass
class DANConfig:
    """Root configuration for D.A.N."""

    core: CoreConfig = field(default_factory=CoreConfig)
    interpret: ProviderConfig = field(
        default_factory=lambda: ProviderConfig(
            name="ollama", model="dan-interp"
        )
    )
    reason: ProviderConfig = field(
        default_factory=lambda: ProviderConfig(
            name="ollama", model="dan-reason"
        )
    )
    persona: ProviderConfig = field(
        default_factory=lambda: ProviderConfig(
            name="ollama", model="dan-persona"
        )
    )
    memory: MemoryConfig = field(default_factory=MemoryConfig)
    skills: SkillsConfig = field(default_factory=SkillsConfig)

    @classmethod
    def from_file(cls, path: Path | str | None = None) -> DANConfig:
        """Load configuration from a YAML file.

        Args:
            path: Path to config file. Uses default if None.

        Returns:
            DANConfig instance.
        """
        path = DEFAULT_CONFIG_FILE if path is None else Path(path)

        if not path.exists():
            logger.info("No config file at %s, using defaults", path)
            return cls()

        try:
            with open(path) as f:
                data = yaml.safe_load(f) or {}
        except Exception:
            logger.exception("Failed to load config from %s", path)
            return cls()

        return cls._from_dict(data)

    @classmethod
    def _from_dict(cls, data: dict[str, Any]) -> DANConfig:
        """Build config from a dictionary."""
        config = cls()

        if "core" in data:
            config.core = CoreConfig(**_filter_fields(CoreConfig, data["core"]))

        if "interpret" in data:
            config.interpret = ProviderConfig(
                **_filter_fields(ProviderConfig, data["interpret"])
            )

        if "reason" in data:
            config.reason = ProviderConfig(
                **_filter_fields(ProviderConfig, data["reason"])
            )

        if "persona" in data:
            config.persona = ProviderConfig(
                **_filter_fields(ProviderConfig, data["persona"])
            )

        if "memory" in data:
            config.memory = MemoryConfig(
                **_filter_fields(MemoryConfig, data["memory"])
            )

        if "skills" in data:
            config.skills = SkillsConfig(
                **_filter_fields(SkillsConfig, data["skills"])
            )

        return config

    def save(self, path: Path | str | None = None) -> None:
        """Save configuration to a YAML file."""
        path = DEFAULT_CONFIG_FILE if path is None else Path(path)

        path.parent.mkdir(parents=True, exist_ok=True)

        data = {
            "core": {
                "threshold": self.core.threshold,
                "log_level": self.core.log_level,
            },
            "interpret": {
                "name": self.interpret.name,
                "model": self.interpret.model,
                "device": self.interpret.device,
                "quantization": self.interpret.quantization,
            },
            "reason": {
                "name": self.reason.name,
                "model": self.reason.model,
                "device": self.reason.device,
                "quantization": self.reason.quantization,
            },
            "persona": {
                "name": self.persona.name,
                "model": self.persona.model,
                "device": self.persona.device,
                "quantization": self.persona.quantization,
            },
            "memory": {
                "short_term_limit": self.memory.short_term_limit,
                "long_term_path": self.memory.long_term_path,
            },
            "skills": {
                "store_path": self.skills.store_path,
                "min_executions": self.skills.min_executions,
                "min_confidence": self.skills.min_confidence,
            },
        }

        with open(path, "w") as f:
            yaml.dump(data, f, default_flow_style=False, sort_keys=False)

        logger.info("Configuration saved to %s", path)

    def ensure_dirs(self) -> None:
        """Create required directories."""
        for path_str in [self.memory.long_term_path, self.skills.store_path]:
            Path(path_str).expanduser().mkdir(parents=True, exist_ok=True)
