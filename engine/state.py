"""Explicit game-state container for V2 games."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameState:
    """Mutable state owned by one game session.

    Only committed moves should be passed to ``record_move``.
    AI simulations, hints, and speculative state changes must not use it.
    """

    game: str
    status: str = "ready"
    data: dict[str, Any] = field(default_factory=dict)
    move_history: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def record_move(self, move: Any) -> None:
        """Record one committed real move."""
        self.move_history.append(move)

    def set_status(self, status: str) -> None:
        if not status.strip():
            raise ValueError("status must not be empty")
        self.status = status

    @property
    def moves(self) -> int:
        return len(self.move_history)
