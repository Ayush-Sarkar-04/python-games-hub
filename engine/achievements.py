"""Achievement persistence."""

from pathlib import Path
from typing import Any

from .persistence import JsonStore

DEFAULT_ACHIEVEMENTS: dict[str, dict[str, Any]] = {}


class AchievementStore:
    def __init__(self, path: str | Path):
        self.store = JsonStore(path)

    def load(self) -> dict[str, dict[str, Any]]:
        data = self.store.load(DEFAULT_ACHIEVEMENTS.copy())
        if not isinstance(data, dict):
            return {}
        return {
            str(achievement_id): dict(record)
            for achievement_id, record in data.items()
            if isinstance(record, dict)
        }

    def save(self, achievements: dict[str, dict[str, Any]]) -> None:
        self.store.save(achievements)
