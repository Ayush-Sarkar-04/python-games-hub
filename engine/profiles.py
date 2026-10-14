"""Player profile persistence and lightweight meta-progression."""

from dataclasses import asdict, dataclass
from pathlib import Path

from .persistence import JsonStore
from .result import GameResult


@dataclass
class Profile:
    name: str = "Player"
    level: int = 1
    xp: int = 0
    unlocked_styles: tuple[str, ...] = ("default",)


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
        styles = data.get("unlocked_styles", ["default"])
        if not isinstance(name, str) or not name.strip():
            name = "Player"
        if not isinstance(level, int) or isinstance(level, bool) or level < 1:
            level = 1
        if not isinstance(xp, int) or isinstance(xp, bool) or xp < 0:
            xp = 0
        if not isinstance(styles, list) or not all(isinstance(style, str) for style in styles):
            styles = ["default"]
        styles = tuple(dict.fromkeys(style for style in styles if style.strip())) or ("default",)
        return Profile(name=name.strip(), level=level, xp=xp, unlocked_styles=styles)

    def save(self, profile: Profile) -> None:
        data = asdict(profile)
        data["unlocked_styles"] = list(profile.unlocked_styles)
        self.store.save(data)


COSMETIC_STYLES = {
    1: "default",
    3: "classic",
    5: "minimal",
    8: "compact",
}


def update_profile(profile: Profile, result: GameResult) -> tuple[Profile, str | None]:
    """Apply simple competitive activity XP and return any newly unlocked style."""
    if result.mode != "competitive" or result.outcome == "quit":
        return profile, None

    xp_gain = 1
    if result.outcome == "win":
        xp_gain += 1

    xp = profile.xp + xp_gain
    level = xp // 10 + 1
    styles = list(profile.unlocked_styles)
    unlocked = None
    for required_level, style in COSMETIC_STYLES.items():
        if level >= required_level and style not in styles:
            styles.append(style)
            unlocked = style

    return Profile(profile.name, level, xp, tuple(styles)), unlocked
