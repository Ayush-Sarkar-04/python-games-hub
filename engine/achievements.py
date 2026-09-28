"""Achievement definitions, evaluation, and persistence."""

from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Callable

from .persistence import JsonStore
from .result import GameResult


@dataclass(frozen=True)
class AchievementDefinition:
    id: str
    name: str
    description: str

    def __post_init__(self) -> None:
        if not self.id.strip():
            raise ValueError("achievement id must not be empty")
        if not self.name.strip():
            raise ValueError("achievement name must not be empty")
        if not self.description.strip():
            raise ValueError("achievement description must not be empty")


AchievementRule = Callable[[GameResult], bool]
ContextAchievementRule = Callable[[GameResult, dict[str, Any]], bool]


class AchievementEvaluator:
    def __init__(
        self,
        definitions: tuple[AchievementDefinition, ...] = (),
        rules: dict[str, AchievementRule] | None = None,
        context_rules: dict[str, ContextAchievementRule] | None = None,
    ):
        self.definitions = definitions
        self.rules = rules or {}
        self.context_rules = context_rules or {}
        definition_ids = {definition.id for definition in definitions}
        if (set(self.rules) | set(self.context_rules)) - definition_ids:
            raise ValueError("Achievement rules must reference defined achievements")

    def evaluate(
        self,
        result: GameResult,
        unlocked: set[str] | None = None,
        context: dict[str, Any] | None = None,
    ) -> list[str]:
        unlocked = unlocked or set()
        context = context or {}
        earned = []
        for definition in self.definitions:
            if definition.id in unlocked:
                continue
            rule = self.rules.get(definition.id)
            context_rule = self.context_rules.get(definition.id)
            if rule and rule(result):
                earned.append(definition.id)
            elif context_rule and context_rule(result, context):
                earned.append(definition.id)
        return earned


BOARD_GAME_ACHIEVEMENT_DEFINITIONS = (
    AchievementDefinition("first_victory", "First Victory", "Win a competitive game for the first time."),
    AchievementDefinition("connect_four_10_win_streak", "Connect Four Streak", "Reach a 10-win competitive Connect Four streak."),
)

BOARD_GAME_ACHIEVEMENT_RULES = {
    "first_victory": lambda result: result.mode == "competitive" and result.outcome == "win",
}

BOARD_GAME_ACHIEVEMENT_CONTEXT_RULES = {
    "connect_four_10_win_streak": lambda result, context: (
        result.game == "connect_four"
        and result.mode == "competitive"
        and result.outcome == "win"
        and context.get("win_streak", 0) >= 10
    ),
}

NON_REAL_TIME_ACHIEVEMENT_DEFINITIONS = (
    AchievementDefinition("perfect_hangman", "Perfect Hangman", "Win a competitive Hangman game with zero mistakes."),
    AchievementDefinition("rps_lizard_spock_win", "Lizard & Spock Victory", "Win a competitive Rock Paper Scissors match using the Lizard & Spock variant."),
    AchievementDefinition("word_scramble_first_try", "Perfect Scramble", "Solve a competitive Word Scramble round on the first attempt."),
)

NON_REAL_TIME_ACHIEVEMENT_RULES = {
    "perfect_hangman": lambda result: (
        result.game == "hangman" and result.mode == "competitive"
        and result.outcome == "win" and result.metadata.get("mistakes") == 0
    ),
    "rps_lizard_spock_win": lambda result: (
        result.game == "rock_paper_scissors" and result.mode == "competitive"
        and result.outcome == "win"
        and result.metadata.get("configuration", {}).get("variant") == "extended"
    ),
    "word_scramble_first_try": lambda result: (
        result.game == "word_scramble" and result.mode == "competitive"
        and result.outcome == "win" and result.metadata.get("attempts") == 1
    ),
}

PROGRESSION_ACHIEVEMENT_DEFINITIONS = (
    AchievementDefinition("snake_200", "Snake 200", "Score more than 200 in a competitive Snake run."),
    AchievementDefinition("all_seven_games", "Full House", "Play all seven games in competitive sessions."),
)

PROGRESSION_ACHIEVEMENT_RULES = {
    "snake_200": lambda result: (
        result.game == "snake" and result.mode == "competitive"
        and (result.score or 0) > 200
    ),
}

PROGRESSION_ACHIEVEMENT_CONTEXT_RULES = {
    "all_seven_games": lambda result, context: (
        result.mode == "competitive"
        and len(context.get("games_played", set())) >= 7
    ),
}

ALL_ACHIEVEMENT_DEFINITIONS = (
    BOARD_GAME_ACHIEVEMENT_DEFINITIONS
    + NON_REAL_TIME_ACHIEVEMENT_DEFINITIONS
    + PROGRESSION_ACHIEVEMENT_DEFINITIONS
)
ALL_ACHIEVEMENT_RULES = {
    **BOARD_GAME_ACHIEVEMENT_RULES,
    **NON_REAL_TIME_ACHIEVEMENT_RULES,
    **PROGRESSION_ACHIEVEMENT_RULES,
}
ALL_ACHIEVEMENT_CONTEXT_RULES = {
    **BOARD_GAME_ACHIEVEMENT_CONTEXT_RULES,
    **PROGRESSION_ACHIEVEMENT_CONTEXT_RULES,
}

BOARD_GAME_ACHIEVEMENT_EVALUATOR = AchievementEvaluator(
    BOARD_GAME_ACHIEVEMENT_DEFINITIONS,
    BOARD_GAME_ACHIEVEMENT_RULES,
    BOARD_GAME_ACHIEVEMENT_CONTEXT_RULES,
)
NON_REAL_TIME_ACHIEVEMENT_EVALUATOR = AchievementEvaluator(
    NON_REAL_TIME_ACHIEVEMENT_DEFINITIONS, NON_REAL_TIME_ACHIEVEMENT_RULES
)
ALL_ACHIEVEMENT_EVALUATOR = AchievementEvaluator(
    ALL_ACHIEVEMENT_DEFINITIONS,
    ALL_ACHIEVEMENT_RULES,
    ALL_ACHIEVEMENT_CONTEXT_RULES,
)


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


def unlock_achievements(
    store: AchievementStore,
    result: GameResult,
    statistics: dict[str, dict[str, Any]],
) -> list[str]:
    records = store.load()
    unlocked = {achievement_id for achievement_id, record in records.items() if record.get("unlocked")}
    earned = ALL_ACHIEVEMENT_EVALUATOR.evaluate(
        result,
        unlocked,
        {
            "games_played": set(statistics),
            "win_streak": statistics.get(result.game, {}).get("win_streak", 0),
        },
    )
    timestamp = datetime.now(timezone.utc).isoformat()
    for achievement_id in earned:
        records[achievement_id] = {
            "unlocked": True,
            "unlocked_at": timestamp,
        }
    if earned:
        store.save(records)
    return earned
