"""Game statistics persistence and competitive result aggregation."""

from pathlib import Path
from typing import Any

from .persistence import JsonStore
from .result import GameResult

DEFAULT_STATISTICS: dict[str, dict[str, Any]] = {}


def update_statistics(
    statistics: dict[str, dict[str, Any]], result: GameResult
) -> dict[str, dict[str, Any]]:
    """Return updated competitive statistics for one completed result."""
    if result.mode != "competitive":
        return statistics

    updated = {game: dict(stats) for game, stats in statistics.items()}
    stats = dict(updated.get(result.game, {}))

    if result.game == "rock_paper_scissors":
        stats["matches"] = stats.get("matches", 0) + 1
        _increment_outcome(stats, result.outcome)
        stats["win_streak"] = result.metadata.get("win_streak", 0)
        stats["best_streak"] = max(stats.get("best_streak", 0), result.metadata.get("best_streak", 0))
        configuration = result.metadata.get("configuration", {})
        personality = configuration.get("personality")
        variant = configuration.get("variant")
        personalities = dict(stats.get("results_by_personality", {}))
        if personality:
            personality_stats = dict(personalities.get(personality, {}))
            _increment_outcome(personality_stats, result.outcome)
            personalities[personality] = personality_stats
        stats["results_by_personality"] = personalities
        stats["lizard_spock_matches"] = stats.get("lizard_spock_matches", 0) + (variant == "extended")

    elif result.game == "hangman":
        stats["games"] = stats.get("games", 0) + 1
        _increment_outcome(stats, result.outcome)
        mistakes = result.metadata.get("mistakes")
        if result.outcome == "win" and isinstance(mistakes, int):
            current = stats.get("fewest_mistakes")
            stats["fewest_mistakes"] = mistakes if current is None else min(current, mistakes)
        stats["win_streak"] = result.metadata.get("win_streak", 0)
        stats["best_streak"] = max(stats.get("best_streak", 0), result.metadata.get("best_streak", 0))

    elif result.game == "word_scramble":
        stats["rounds"] = stats.get("rounds", 0) + 1
        _increment_outcome(stats, result.outcome)
        attempts = result.metadata.get("attempts")
        if result.outcome == "win" and isinstance(attempts, int):
            current = stats.get("fewest_attempts")
            stats["fewest_attempts"] = attempts if current is None else min(current, attempts)
        stats["win_streak"] = result.metadata.get("win_streak", 0)
        stats["best_streak"] = max(stats.get("best_streak", 0), result.metadata.get("best_streak", 0))

    else:
        return statistics

    updated[result.game] = stats
    return updated


def _increment_outcome(stats: dict[str, Any], outcome: str) -> None:
    if outcome == "win":
        stats["wins"] = stats.get("wins", 0) + 1
    elif outcome == "loss":
        stats["losses"] = stats.get("losses", 0) + 1
    elif outcome == "draw":
        stats["draws"] = stats.get("draws", 0) + 1


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
