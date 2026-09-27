"""Shared result model for game sessions."""

from dataclasses import dataclass, field
from typing import Any

VALID_OUTCOMES = {"win", "loss", "draw", "quit", "game_over"}
CONFIGURATION_KEYS = {"custom_settings", "personality", "variant"}


@dataclass(frozen=True)
class GameResult:
    """Result of one competitive game/session or one game run."""

    game: str
    outcome: str
    difficulty: str
    mode: str
    score: int | None = None
    moves: int | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.game.strip():
            raise ValueError("game must not be empty")
        if self.outcome not in VALID_OUTCOMES:
            raise ValueError(f"Unsupported outcome: {self.outcome}")
        if not self.difficulty.strip():
            raise ValueError("difficulty must not be empty")
        if not self.mode.strip():
            raise ValueError("mode must not be empty")
        if self.score is not None and (
            isinstance(self.score, bool) or not isinstance(self.score, int)
        ):
            raise TypeError("score must be an integer or None")
        if self.moves is not None and (
            isinstance(self.moves, bool) or not isinstance(self.moves, int)
        ):
            raise TypeError("moves must be an integer or None")
        if not isinstance(self.metadata, dict):
            raise TypeError("metadata must be a dictionary")
        configuration = self.metadata.get("configuration", {})
        if not isinstance(configuration, dict):
            raise TypeError("metadata['configuration'] must be a dictionary")
        misplaced = CONFIGURATION_KEYS.intersection(self.metadata)
        if misplaced:
            raise ValueError(
                "configuration fields must be nested under metadata['configuration']"
            )

    def with_metadata(self, **updates: Any) -> "GameResult":
        """Return a copy with additional metadata."""
        metadata = dict(self.metadata)
        configuration = dict(metadata.get("configuration", {}))
        for key, value in updates.items():
            if key in CONFIGURATION_KEYS:
                configuration[key] = value
            else:
                metadata[key] = value
        if configuration:
            metadata["configuration"] = configuration
        return GameResult(
            game=self.game,
            outcome=self.outcome,
            difficulty=self.difficulty,
            mode=self.mode,
            score=self.score,
            moves=self.moves,
            metadata=metadata,
        )
