"""Mastermind game implementation for the Game Hub."""

import random

from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import display_title


DIFFICULTIES = {
    "easy": {"name": "Easy", "length": 4, "colors": ("R", "G", "B", "Y"), "attempts": 10},
    "medium": {"name": "Medium", "length": 4, "colors": ("R", "G", "B", "Y", "O", "P"), "attempts": 10},
    "hard": {"name": "Hard", "length": 5, "colors": ("R", "G", "B", "Y", "O", "P"), "attempts": 10},
}


def generate_code(difficulty: str) -> tuple[str, ...]:
    settings = DIFFICULTIES[difficulty]
    return tuple(random.sample(settings["colors"], settings["length"]))


def evaluate_guess(code: tuple[str, ...], guess: tuple[str, ...]) -> tuple[int, int]:
    """Return exact matches and correct-color/wrong-position matches."""
    exact = sum(a == b for a, b in zip(code, guess))
    remaining_code = [a for a, b in zip(code, guess) if a != b]
    remaining_guess = [b for a, b in zip(code, guess) if a != b]
    misplaced = sum(
        min(remaining_code.count(color), remaining_guess.count(color))
        for color in set(remaining_code)
    )
    return exact, misplaced


def validate_guess(guess: str, difficulty: str) -> tuple[str, ...]:
    settings = DIFFICULTIES[difficulty]
    normalized = tuple(part.strip().upper() for part in guess.replace(",", " ").split())
    if len(normalized) != settings["length"]:
        raise ValueError(f"Enter exactly {settings['length']} colors.")
    if any(color not in settings["colors"] for color in normalized):
        raise ValueError("Guess contains a color that is not available.")
    if len(set(normalized)) != len(normalized):
        raise ValueError("Do not repeat colors in a code.")
    return normalized


class MastermindGame:
    name = "Mastermind"
    description = "Crack the hidden color code"

    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "mastermind":
            raise ValueError("MastermindGame requires game='mastermind'")
        if config.difficulty not in DIFFICULTIES:
            raise ValueError(f"Unsupported Mastermind difficulty: {config.difficulty}")
        code = tuple(config.options.get("code", ())) or generate_code(config.difficulty)
        settings = DIFFICULTIES[config.difficulty]
        if len(code) != settings["length"] or len(set(code)) != len(code) or any(
            color not in settings["colors"] for color in code
        ):
            raise ValueError("Invalid Mastermind code.")
        return GameState(
            game="mastermind",
            data={
                "code": code,
                "attempts": 0,
                "max_attempts": settings["attempts"],
                "history": [],
                "score": 0,
            },
        )

    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        state.set_status("playing")
        settings = DIFFICULTIES[config.difficulty]
        display_title("MASTERMIND")
        print(f"Difficulty: {settings['name']}")
        print(f"Colors: {' '.join(settings['colors'])}")
        print(f"Code length: {settings['length']} | Attempts: {settings['attempts']}")
        while state.data["attempts"] < state.data["max_attempts"]:
            raw = input("\nGuess: ").strip()
            try:
                guess = validate_guess(raw, config.difficulty)
            except ValueError as exc:
                print(exc)
                continue
            exact, misplaced = evaluate_guess(state.data["code"], guess)
            state.data["attempts"] += 1
            state.record_move({"guess": guess, "exact": exact, "misplaced": misplaced})
            state.data["history"].append((guess, exact, misplaced))
            if exact == len(state.data["code"]):
                state.data["score"] = (state.data["max_attempts"] - state.data["attempts"] + 1) * 10
                return self._finish(state, config, "win")
            print(f"Exact: {exact} | Misplaced: {misplaced}")
        return self._finish(state, config, "loss")

    def _finish(self, state, config, outcome):
        state.set_status(outcome)
        return GameResult(
            game="mastermind",
            outcome=outcome,
            difficulty=config.difficulty,
            mode=config.mode,
            score=state.data["score"],
            moves=state.moves,
            metadata={
                "attempts": state.data["attempts"],
                "configuration": {
                    "code_length": len(state.data["code"]),
                    "max_attempts": state.data["max_attempts"],
                    "colors": DIFFICULTIES[config.difficulty]["colors"],
                },
            },
        )


def main():
    game = MastermindGame()
    difficulty = {"1": "easy", "2": "medium", "3": "hard"}.get(
        input("Difficulty (1 Easy, 2 Medium, 3 Hard): ").strip()
    )
    if not difficulty:
        print("Invalid difficulty.")
        return
    config = SessionConfig(game="mastermind", difficulty=difficulty)
    game.play(game.setup(config), config)


if __name__ == "__main__":
    main()
