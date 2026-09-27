"""Settings persistence foundation."""

from pathlib import Path
from typing import Any

from .persistence import JsonStore

DEFAULT_SETTINGS: dict[str, Any] = {
    "banner_style": "default",
    "auto_suggest_difficulty": True,
}


class SettingsStore:
    def __init__(self, path: str | Path):
        self.store = JsonStore(path)

    def load(self) -> dict[str, Any]:
        data = self.store.load(DEFAULT_SETTINGS.copy())
        if not isinstance(data, dict):
            return dict(DEFAULT_SETTINGS)
        settings = dict(DEFAULT_SETTINGS)
        settings.update(data)
        return settings

    def save(self, settings: dict[str, Any]) -> None:
        self.store.save(settings)
