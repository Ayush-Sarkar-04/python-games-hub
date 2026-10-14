"""Mutable state container for a game session."""

from dataclasses import dataclass, field
from typing import Any


@dataclass
class GameState:
    """Mutable state owned by one game session."""

    game: str
    status: str = "ready"
    data: dict[str, Any] = field(default_factory=dict)
    move_history: list[Any] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    def record_move(self, move: Any) -> None:
        self.move_history.append(move)

    def set_status(self, status: str) -> None:
        if not status.strip():
            raise ValueError("status must not be empty")
        self.status = status

    @property
    def moves(self) -> int:
        return len(self.move_history)
