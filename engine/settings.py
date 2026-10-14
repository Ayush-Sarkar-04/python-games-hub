"""Application settings persistence and validation."""

from pathlib import Path
from typing import Any

from .persistence import JsonStore

DEFAULT_SETTINGS: dict[str, Any] = {
    "banner_style": "default",
    "auto_suggest_difficulty": True,
}

VALID_BANNER_STYLES = {"default", "classic", "minimal", "compact"}


def normalize_settings(data: dict[str, Any] | None) -> dict[str, Any]:
    settings = dict(DEFAULT_SETTINGS)
    if not isinstance(data, dict):
        return settings
    banner = data.get("banner_style")
    if isinstance(banner, str) and banner in VALID_BANNER_STYLES:
        settings["banner_style"] = banner
    auto = data.get("auto_suggest_difficulty")
    if isinstance(auto, bool):
        settings["auto_suggest_difficulty"] = auto
    return settings


class SettingsStore:
    def __init__(self, path: str | Path):
        self.store = JsonStore(path)

    def load(self) -> dict[str, Any]:
        return normalize_settings(self.store.load({}))

    def save(self, settings: dict[str, Any]) -> None:
        self.store.save(normalize_settings(settings))
