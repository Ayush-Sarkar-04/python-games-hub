"""Profile persistence foundation."""

from dataclasses import asdict, dataclass
from pathlib import Path

from .persistence import JsonStore


@dataclass
class Profile:
    name: str = "Player"
    level: int = 1
    xp: int = 0


class ProfileStore:
    def __init__(self, path: str | Path):
        self.store = JsonStore(path)

    def load(self) -> Profile:
        data = self.store.load({})
        if not isinstance(data, dict):
            return Profile()
        name = data.get("name", "Player")
        level = data.get("level", 1)
        xp = data.get("xp", 0)
        if not isinstance(name, str) or not name.strip():
            name = "Player"
        if not isinstance(level, int) or isinstance(level, bool) or level < 1:
            level = 1
        if not isinstance(xp, int) or isinstance(xp, bool) or xp < 0:
            xp = 0
        return Profile(name=name.strip(), level=level, xp=xp)

    def save(self, profile: Profile) -> None:
        self.store.save(asdict(profile))
