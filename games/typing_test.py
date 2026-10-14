"""Typing Test game implementation for the Game Hub."""

import random
import time

from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import display_title


DIFFICULTIES = {
    "easy": {
        "name": "Easy",
        "duration": 30,
        "texts": (
            "The quick brown fox jumps over the lazy dog.",
            "Practice makes progress. Keep your hands relaxed and type with steady rhythm.",
        ),
    },
    "medium": {
        "name": "Medium",
        "duration": 30,
        "texts": (
            "Good typing is less about speed at first and more about accuracy, rhythm, and consistency.",
            "Small improvements become meaningful when you practice regularly and focus on clean keystrokes.",
        ),
    },
    "hard": {
        "name": "Hard",
        "duration": 30,
        "texts": (
            "Reliable performance comes from maintaining accuracy while processing punctuation, capitalization, and changing sentence structure.",
            "A disciplined typist does not chase every extra word per minute; instead, they build repeatable accuracy under pressure.",
        ),
    },
}


def calculate_metrics(target: str, typed: str, elapsed_seconds: float) -> dict:
    """Return accuracy, WPM, correct characters, and score for a typing attempt."""
    elapsed = max(float(elapsed_seconds), 0.001)
    typed = typed[:]
    correct = sum(
        1 for index, character in enumerate(typed)
        if index < len(target) and character == target[index]
    )
    accuracy = (correct / len(typed) * 100) if typed else 0.0
    wpm = (correct / 5) / (elapsed / 60)
    score = round(wpm * (accuracy / 100))
    return {
        "correct_characters": correct,
        "typed_characters": len(typed),
        "accuracy": round(accuracy, 2),
        "wpm": round(wpm, 2),
        "score": score,
    }


class TypingTestGame:
    name = "Typing Test"
    description = "Measure typing speed and accuracy"

    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "typing_test":
            raise ValueError("TypingTestGame requires game='typing_test'")
        if config.difficulty not in DIFFICULTIES:
            raise ValueError(f"Unsupported Typing Test difficulty: {config.difficulty}")
        settings = DIFFICULTIES[config.difficulty]
        text = config.options.get("text") or random.choice(settings["texts"])
        if not isinstance(text, str) or not text.strip():
            raise ValueError("text must be a non-empty string")
        return GameState(
            game="typing_test",
            data={
                "text": text,
                "duration": settings["duration"],
                "typed": "",
                "elapsed_seconds": 0.0,
                "metrics": None,
                "score": 0,
            },
        )

    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        state.set_status("playing")
        target = state.data["text"]
        display_title("TYPING TEST")
        print(f"Difficulty: {DIFFICULTIES[config.difficulty]['name']}")
        print(f"Time limit: {state.data['duration']} seconds")
        print("\nType the passage below, then press Enter.")
        print(f"\n{target}\n")
        started = time.monotonic()
        typed = input("Type: ")
        elapsed = min(time.monotonic() - started, state.data["duration"])
        state.data["typed"] = typed
        state.data["elapsed_seconds"] = elapsed
        state.record_move({"typed_characters": len(typed), "elapsed_seconds": elapsed})
        state.data["metrics"] = calculate_metrics(target, typed, elapsed)
        state.data["score"] = state.data["metrics"]["score"]
        state.set_status("finished")
        return GameResult(
            game="typing_test",
            outcome="finished",
            difficulty=config.difficulty,
            mode=config.mode,
            score=state.data["score"],
            moves=state.moves,
            metadata={
                **state.data["metrics"],
                "elapsed_seconds": round(elapsed, 2),
                "configuration": {"duration": state.data["duration"]},
            },
        )


def main():
    game = TypingTestGame()
    difficulty = {"1": "easy", "2": "medium", "3": "hard"}.get(
        input("Difficulty (1 Easy, 2 Medium, 3 Hard): ").strip()
    )
    if not difficulty:
        print("Invalid difficulty.")
        return
    config = SessionConfig(game="typing_test", difficulty=difficulty)
    game.play(game.setup(config), config)


if __name__ == "__main__":
    main()
