"""Lightweight provisional game contract and session configuration."""

from dataclasses import dataclass, field
from typing import Any, Protocol

from .result import GameResult
from .state import GameState


@dataclass
class SessionConfig:
    """Configuration selected by the hub for one game session."""

    game: str
    difficulty: str = "medium"
    mode: str = "competitive"
    custom_settings: dict[str, Any] = field(default_factory=dict)
    options: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if not self.game.strip():
            raise ValueError("game must not be empty")
        if not self.difficulty.strip():
            raise ValueError("difficulty must not be empty")
        if not self.mode.strip():
            raise ValueError("mode must not be empty")
        if self.mode not in {"competitive", "practice"}:
            raise ValueError("mode must be 'competitive' or 'practice'")
        if not isinstance(self.custom_settings, dict):
            raise TypeError("custom_settings must be a dictionary")
        if not isinstance(self.options, dict):
            raise TypeError("options must be a dictionary")

    @property
    def is_competitive(self) -> bool:
        return self.mode == "competitive"


class Game(Protocol):
    """Provisional V2 game contract.

    This contract is intentionally small. It will be validated with
    Tic-Tac-Toe and Connect Four before it is frozen.
    """

    name: str
    description: str

    def setup(self, config: SessionConfig) -> GameState:
        ...

    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        ...
