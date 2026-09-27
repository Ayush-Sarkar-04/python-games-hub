"""Statistics persistence foundation.

Competitive statistics are intentionally game-appropriate. Consumers must not
assume every game uses win/loss/draw-shaped outcomes.
"""

from pathlib import Path
from typing import Any

from .persistence import JsonStore

DEFAULT_STATISTICS: dict[str, dict[str, Any]] = {}


class StatisticsStore:
    def __init__(self, path: str | Path):
        self.store = JsonStore(path)

    def load(self) -> dict[str, dict[str, Any]]:
        data = self.store.load(DEFAULT_STATISTICS.copy())
        if not isinstance(data, dict):
            return {}
        return {
            str(game): dict(stats)
            for game, stats in data.items()
            if isinstance(stats, dict)
        }

    def save(self, statistics: dict[str, dict[str, Any]]) -> None:
        self.store.save(statistics)
