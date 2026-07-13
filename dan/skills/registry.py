from __future__ import annotations

import json
import logging
from pathlib import Path

from dan.skills.skill import Skill

logger = logging.getLogger(__name__)


class SkillRegistry:
    """Registry for learned skills.

    Stores and retrieves skills, matching user intent to learned patterns.
    Persisted to a JSON file.
    """

    def __init__(self, storage_path: Path | None = None) -> None:
        self._storage_path = storage_path or Path("dan_skills.json")
        self._skills: dict[str, Skill] = {}
        self._load()

    def _load(self) -> None:
        """Load skills from disk."""
        if self._storage_path.exists():
            try:
                data = json.loads(self._storage_path.read_text())
                for skill_data in data:
                    skill = Skill.from_dict(skill_data)
                    self._skills[skill.name] = skill
                logger.debug("Loaded %d skills", len(self._skills))
            except Exception:
                logger.exception("Failed to load skills")

    def _save(self) -> None:
        """Persist skills to disk."""
        data = [skill.to_dict() for skill in self._skills.values()]
        try:
            self._storage_path.write_text(json.dumps(data, indent=2))
        except Exception:
            logger.exception("Failed to save skills")

    def register(self, skill: Skill) -> None:
        """Register a new skill."""
        self._skills[skill.name] = skill
        self._save()
        logger.debug("Registered skill: %s", skill.name)

    def get(self, name: str) -> Skill | None:
        """Get a skill by name."""
        return self._skills.get(name)

    def remove(self, name: str) -> bool:
        """Remove a skill. Returns True if removed."""
        if name in self._skills:
            del self._skills[name]
            self._save()
            return True
        return False

    def match(self, message: str) -> Skill | None:
        """Match a message to the best skill.

        Uses intent matching and example similarity.
        Returns the best matching skill or None.
        """
        best_skill: Skill | None = None
        best_score = 0.0

        message_lower = message.lower().strip()

        for skill in self._skills.values():
            score = self._score_skill(skill, message_lower)
            if score > best_score:
                best_score = score
                best_skill = skill

        return best_skill if best_score > 0.5 else None

    def _score_skill(self, skill: Skill, message: str) -> float:
        """Score how well a skill matches a message."""
        score = 0.0

        # Intent matching
        intent_lower = skill.intent.lower()
        if intent_lower in message:
            score += 0.7

        # Example matching
        for example in skill.examples:
            if example.lower() in message:
                score += 0.2
                break

        # Success rate bonus
        score += skill.success_rate * 0.1

        return min(score, 1.0)

    def list_skills(self) -> list[Skill]:
        """List all registered skills."""
        return list(self._skills.values())

    def names(self) -> list[str]:
        """List all skill names."""
        return list(self._skills.keys())
