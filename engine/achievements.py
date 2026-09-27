"""Achievement definitions, evaluation, and persistence."""

from dataclasses import dataclass
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


class AchievementEvaluator:
    """Evaluate achievement definitions against one game result."""

    def __init__(
        self,
        definitions: tuple[AchievementDefinition, ...] = (),
        rules: dict[str, AchievementRule] | None = None,
    ):
        self.definitions = definitions
        self.rules = rules or {}
        definition_ids = {definition.id for definition in definitions}
        if set(self.rules) - definition_ids:
            raise ValueError("Achievement rules must reference defined achievements")

    def evaluate(self, result: GameResult, unlocked: set[str] | None = None) -> list[str]:
        unlocked = unlocked or set()
        return [
            definition.id
            for definition in self.definitions
            if definition.id not in unlocked
            and self.rules.get(definition.id, lambda _: False)(result)
        ]


BOARD_GAME_ACHIEVEMENT_DEFINITIONS = (
    AchievementDefinition(
        id="first_victory",
        name="First Victory",
        description="Win a competitive game for the first time.",
    ),
    AchievementDefinition(
        id="connect_four_10_win_streak",
        name="Connect Four Streak",
        description="Reach a 10-win competitive Connect Four streak.",
    ),
)


BOARD_GAME_ACHIEVEMENT_RULES: dict[str, AchievementRule] = {
    "first_victory": lambda result: result.mode == "competitive" and result.outcome == "win",
    "connect_four_10_win_streak": lambda result: (
        result.game == "connect_four"
        and result.mode == "competitive"
        and result.outcome == "win"
        and result.metadata.get("win_streak", 0) >= 10
    ),
}

BOARD_GAME_ACHIEVEMENT_EVALUATOR = AchievementEvaluator(
    definitions=BOARD_GAME_ACHIEVEMENT_DEFINITIONS,
    rules=BOARD_GAME_ACHIEVEMENT_RULES,
)


NON_REAL_TIME_ACHIEVEMENT_DEFINITIONS = (
    AchievementDefinition(
        id="perfect_hangman",
        name="Perfect Hangman",
        description="Win a competitive Hangman game with zero mistakes.",
    ),
    AchievementDefinition(
        id="rps_lizard_spock_win",
        name="Lizard & Spock Victory",
        description="Win a competitive Rock Paper Scissors match using the Lizard & Spock variant.",
    ),
    AchievementDefinition(
        id="word_scramble_first_try",
        name="Perfect Scramble",
        description="Solve a competitive Word Scramble round on the first attempt.",
    ),
)

NON_REAL_TIME_ACHIEVEMENT_RULES: dict[str, AchievementRule] = {
    "perfect_hangman": lambda result: (
        result.game == "hangman"
        and result.mode == "competitive"
        and result.outcome == "win"
        and result.metadata.get("mistakes") == 0
    ),
    "rps_lizard_spock_win": lambda result: (
        result.game == "rock_paper_scissors"
        and result.mode == "competitive"
        and result.outcome == "win"
        and result.metadata.get("configuration", {}).get("variant") == "extended"
    ),
    "word_scramble_first_try": lambda result: (
        result.game == "word_scramble"
        and result.mode == "competitive"
        and result.outcome == "win"
        and result.metadata.get("attempts") == 1
    ),
}

NON_REAL_TIME_ACHIEVEMENT_EVALUATOR = AchievementEvaluator(
    definitions=NON_REAL_TIME_ACHIEVEMENT_DEFINITIONS,
    rules=NON_REAL_TIME_ACHIEVEMENT_RULES,
)

ALL_ACHIEVEMENT_DEFINITIONS = BOARD_GAME_ACHIEVEMENT_DEFINITIONS + NON_REAL_TIME_ACHIEVEMENT_DEFINITIONS
ALL_ACHIEVEMENT_RULES = {**BOARD_GAME_ACHIEVEMENT_RULES, **NON_REAL_TIME_ACHIEVEMENT_RULES}
ALL_ACHIEVEMENT_EVALUATOR = AchievementEvaluator(
    definitions=ALL_ACHIEVEMENT_DEFINITIONS,
    rules=ALL_ACHIEVEMENT_RULES,
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
