"""Python Games Hub V2 foundation shell.

Sprint 1 establishes the hub architecture. Game modules are migrated in later
sprints; the registry deliberately uses stable game identifiers rather than
menu positions.
"""

from dataclasses import dataclass

from engine.game import SessionConfig
from engine.utils import choose_from_menu, display_title


@dataclass(frozen=True)
class GameDefinition:
    name: str
    description: str
    module: str
    capabilities: frozenset[str]
    modes: frozenset[str]
    difficulties: tuple[str, ...]


GAME_REGISTRY = {
    "tic_tac_toe": GameDefinition(
        "Tic-Tac-Toe",
        "Classic 3x3 strategy game",
        "tic_tac_toe",
        frozenset({"replay", "history", "hint", "practice", "custom_difficulty"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard", "custom"),
    ),
    "hangman": GameDefinition(
        "Hangman",
        "Guess the hidden word before you run out of attempts",
        "hangman",
        frozenset({"hint", "practice", "custom_difficulty"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard", "custom"),
    ),
    "rock_paper_scissors": GameDefinition(
        "Rock Paper Scissors",
        "Classic RPS with optional Lizard & Spock",
        "rock_paper_scissors",
        frozenset({"history", "practice"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
    ),
    "word_scramble": GameDefinition(
        "Word Scramble",
        "Unscramble words across multiple difficulty levels",
        "word_scramble",
        frozenset({"hint", "practice"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
    ),
    "connect_four": GameDefinition(
        "Connect Four",
        "Connect four pieces before your opponent",
        "connect_four",
        frozenset({"replay", "history", "hint", "practice", "custom_difficulty"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard", "custom"),
    ),
    "snake": GameDefinition(
        "Snake",
        "Classic terminal Snake with score-based play",
        "snake",
        frozenset({"run_history", "practice"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
    ),
}


def build_session_config(
    game: str,
    difficulty: str,
    mode: str = "competitive",
    custom_settings: dict | None = None,
    options: dict | None = None,
) -> SessionConfig:
    """Build and validate one hub-owned session configuration."""
    if game not in GAME_REGISTRY:
        raise ValueError(f"Unknown game: {game}")

    definition = GAME_REGISTRY[game]

    if difficulty == "custom" and "custom_difficulty" not in definition.capabilities:
        raise ValueError(f"{game} does not support custom difficulty")

    if difficulty not in definition.difficulties:
        raise ValueError(f"Unsupported difficulty for {game}: {difficulty}")

    if mode not in definition.modes:
        raise ValueError(f"Unsupported mode for {game}: {mode}")

    return SessionConfig(
        game=game,
        difficulty=difficulty,
        mode=mode,
        custom_settings=custom_settings or {},
        options=options or {},
    )


def display_game_menu() -> None:
    display_title("PYTHON GAMES HUB")
    print("1. Play")
    print("2. Quick Play")
    print("3. Profile & Statistics")
    print("4. Settings")
    print("5. Exit")


def choose_game(*, input_func=input) -> str:
    """Let the hub select a game using its stable registry identifier."""
    print("\nChoose Game")

    entries = list(GAME_REGISTRY.items())

    for number, (_, definition) in enumerate(entries, 1):
        print(f"{number}. {definition.name}")

    choice = choose_from_menu(
        "Choose: ",
        [str(number) for number in range(1, len(entries) + 1)],
        input_func=input_func,
    )

    return entries[int(choice) - 1][0]


def choose_session_config(game: str, *, input_func=input) -> SessionConfig:
    """Choose a named difficulty for a hub-owned session configuration."""
    if game not in GAME_REGISTRY:
        raise ValueError(f"Unknown game: {game}")

    definition = GAME_REGISTRY[game]

    print(f"\nConfigure Session: {definition.name}")
    print("1. Easy")
    print("2. Medium")
    print("3. Hard")

    if "custom_difficulty" in definition.capabilities:
        print("4. Advanced")
        valid_choices = {"1", "2", "3", "4"}
    else:
        valid_choices = {"1", "2", "3"}

    difficulty_choice = choose_from_menu(
        "Choose difficulty: ",
        valid_choices,
        input_func=input_func,
    )

    if difficulty_choice == "4":
        raise NotImplementedError(
            "Advanced custom configuration is implemented in Sprint 3."
        )

    difficulty = {
        "1": "easy",
        "2": "medium",
        "3": "hard",
    }[difficulty_choice]

    return build_session_config(game, difficulty)


def main() -> None:
    """Run the Sprint 1 V2 foundation shell."""
    while True:
        display_game_menu()

        choice = choose_from_menu(
            "Choose an option: ",
            {"1", "2", "3", "4", "5"},
        )

        if choice == "1":
            game = choose_game()

            try:
                choose_session_config(game)
            except NotImplementedError as exc:
                print(f"\n{exc}")

            print("\nGame migration is scheduled for Sprint 2.")
            input("Press Enter to return to the hub...")

        elif choice == "2":
            print("\nQuick Play will be connected after game migration.")
            input("Press Enter to return to the hub...")

        elif choice == "3":
            print("\nProfile & Statistics foundation is ready.")
            input("Press Enter to return to the hub...")

        elif choice == "4":
            print("\nSettings foundation is ready.")
            input("Press Enter to return to the hub...")

        else:
            print("\nV2 foundation session ended.")
            break


if __name__ == "__main__":
    main()
