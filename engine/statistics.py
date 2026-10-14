"""Competitive statistics aggregation and difficulty suggestions."""

from pathlib import Path
from typing import Any

from .persistence import JsonStore
from .result import GameResult

DEFAULT_STATISTICS: dict[str, dict[str, Any]] = {}


def _copy_statistics(statistics):
    return {game: dict(stats) for game, stats in statistics.items()}


def _increment_outcome(stats, outcome):
    if outcome == "win":
        stats["wins"] = stats.get("wins", 0) + 1
    elif outcome == "loss":
        stats["losses"] = stats.get("losses", 0) + 1
    elif outcome == "draw":
        stats["draws"] = stats.get("draws", 0) + 1


def _record_recent(stats, result):
    recent = list(stats.get("recent_results", []))
    recent.append({
        "difficulty": result.difficulty,
        "outcome": result.outcome,
        "score": result.score,
    })
    stats["recent_results"] = recent[-10:]


def _record_streak(stats, result):
    # Competitive wins build the streak; losses and draws break it.
    if result.outcome == "win":
        stats["win_streak"] = stats.get("win_streak", 0) + 1
    else:
        stats["win_streak"] = 0
    stats["best_streak"] = max(
        stats.get("best_streak", 0),
        stats["win_streak"],
    )


def _record_board(stats, result):
    stats["games"] = stats.get("games", 0) + 1
    _increment_outcome(stats, result.outcome)
    stats["total_moves"] = stats.get("total_moves", 0) + (result.moves or 0)
    _record_streak(stats, result)


def update_statistics(statistics: dict[str, dict[str, Any]], result: GameResult):
    if result.mode != "competitive" or result.outcome == "quit":
        return statistics

    updated = _copy_statistics(statistics)
    stats = dict(updated.get(result.game, {}))

    if result.game == "tic_tac_toe":
        _record_board(stats, result)

    elif result.game == "connect_four":
        _record_board(stats, result)

    elif result.game == "rock_paper_scissors":
        stats["matches"] = stats.get("matches", 0) + 1
        _increment_outcome(stats, result.outcome)
        _record_streak(stats, result)
        configuration = result.metadata.get("configuration", {})
        personality = configuration.get("personality")
        personalities = dict(stats.get("results_by_personality", {}))
        if personality:
            personality_stats = dict(personalities.get(personality, {}))
            _increment_outcome(personality_stats, result.outcome)
            personalities[personality] = personality_stats
        stats["results_by_personality"] = personalities
        stats["lizard_spock_matches"] = stats.get("lizard_spock_matches", 0) + (
            configuration.get("variant") == "extended"
        )

    elif result.game == "hangman":
        stats["games"] = stats.get("games", 0) + 1
        _increment_outcome(stats, result.outcome)
        mistakes = result.metadata.get("mistakes")
        if result.outcome == "win" and isinstance(mistakes, int):
            current = stats.get("fewest_mistakes")
            stats["fewest_mistakes"] = mistakes if current is None else min(current, mistakes)
        _record_streak(stats, result)

    elif result.game == "word_scramble":
        stats["rounds"] = stats.get("rounds", 0) + 1
        _increment_outcome(stats, result.outcome)
        attempts = result.metadata.get("attempts")
        if result.outcome == "win" and isinstance(attempts, int):
            current = stats.get("fewest_attempts")
            stats["fewest_attempts"] = attempts if current is None else min(current, attempts)
        stats["total_score"] = stats.get("total_score", 0) + (result.score or 0)
        _record_streak(stats, result)

    elif result.game == "snake":
        stats["games"] = stats.get("games", 0) + 1
        stats["total_score"] = stats.get("total_score", 0) + (result.score or 0)
        stats["best_score"] = max(stats.get("best_score", 0), result.score or 0)
        top_runs = list(stats.get("top_runs", []))
        top_runs.append({
            "score": result.score or 0,
            "difficulty": result.difficulty,
            "outcome": result.outcome,
        })
        stats["top_runs"] = sorted(top_runs, key=lambda run: run["score"], reverse=True)[:5]

    elif result.game == "minesweeper":
        stats["games"] = stats.get("games", 0) + 1
        _increment_outcome(stats, result.outcome)
        stats["total_score"] = stats.get("total_score", 0) + (result.score or 0)
        stats["best_score"] = max(stats.get("best_score", 0), result.score or 0)
        _record_streak(stats, result)

    elif result.game == "typing_test":
        stats["tests"] = stats.get("tests", 0) + 1
        stats["best_wpm"] = max(stats.get("best_wpm", 0), result.metadata.get("wpm", 0))
        stats["best_accuracy"] = max(stats.get("best_accuracy", 0), result.metadata.get("accuracy", 0))
        stats["total_score"] = stats.get("total_score", 0) + (result.score or 0)

    elif result.game == "mastermind":
        stats["games"] = stats.get("games", 0) + 1
        _increment_outcome(stats, result.outcome)
        stats["total_score"] = stats.get("total_score", 0) + (result.score or 0)
        stats["best_score"] = max(stats.get("best_score", 0), result.score or 0)
        _record_streak(stats, result)

    else:
        return statistics

    _record_recent(stats, result)
    updated[result.game] = stats
    return updated


def suggest_difficulty(game: str, statistics: dict[str, dict[str, Any]]) -> str | None:
    """Return an advisory difficulty based on the last ten competitive results."""
    stats = statistics.get(game, {})
    recent = stats.get("recent_results", [])
    if len(recent) < 5:
        return None

    medium = [item for item in recent if item.get("difficulty") == "medium"]
    hard = [item for item in recent if item.get("difficulty") == "hard"]
    easy = [item for item in recent if item.get("difficulty") == "easy"]

    if len(medium) >= 5 and sum(item.get("outcome") == "win" for item in medium[-10:]) >= 4:
        return "hard"
    if len(hard) >= 5 and sum(item.get("outcome") == "win" for item in hard[-10:]) <= 2:
        return "medium"
    if len(easy) >= 5 and sum(item.get("outcome") == "win" for item in easy[-10:]) >= 4:
        return "medium"
    return None


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
