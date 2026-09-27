from dataclasses import dataclass, replace
from engine.game import SessionConfig
from engine.utils import choose_from_menu, display_title
from games.tic_tac_toe import TicTacToeGame
from games.connect_four import ConnectFourGame
from games.hangman import HangmanGame
from games.rock_paper_scissors import RockPaperScissorsGame
from games.word_scramble import WordScrambleGame
from games.snake import SnakeGame
@dataclass(frozen=True)
class GameDefinition:
    name: str
    description: str
    module: str
    capabilities: frozenset[str]
    modes: frozenset[str]
    difficulties: tuple[str, ...]
    configuration_options: frozenset[str] = frozenset()
GAME_REGISTRY = {
    "tic_tac_toe": GameDefinition(
        "Tic-Tac-Toe",
        "Classic 3x3 strategy game",
        "games.tic_tac_toe",
        frozenset({"replay", "history", "hint", "practice", "custom_difficulty"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
        frozenset({"player_mode", "personality"}),
    ),
    "hangman": GameDefinition(
        "Hangman",
        "Guess the hidden word before you run out of attempts",
        "games.hangman",
        frozenset({"hint", "practice"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
        frozenset({"category"}),
    ),
    "rock_paper_scissors": GameDefinition(
        "Rock Paper Scissors",
        "Classic RPS with optional Lizard & Spock",
        "games.rock_paper_scissors",
        frozenset({"history", "practice"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
        frozenset({"variant", "match_type", "rounds"}),
    ),
    "word_scramble": GameDefinition(
        "Word Scramble",
        "Unscramble words across multiple difficulty levels",
        "games.word_scramble",
        frozenset({"hint", "practice"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
        frozenset(),
    ),
    "connect_four": GameDefinition(
        "Connect Four",
        "Connect four pieces before your opponent",
        "games.connect_four",
        frozenset({"replay", "history", "hint", "practice", "custom_difficulty"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
        frozenset({"player_mode", "first_player"}),
    ),
    "snake": GameDefinition(
        "Snake",
        "Classic terminal Snake with score-based play",
        "games.snake",
        frozenset({"run_history", "practice"}),
        frozenset({"competitive", "practice"}),
        ("easy", "medium", "hard"),
        frozenset({"wrap"}),
    ),
}

GAME_CLASSES = {
    "tic_tac_toe": TicTacToeGame,
    "connect_four": ConnectFourGame,
    "hangman": HangmanGame,
    "rock_paper_scissors": RockPaperScissorsGame,
    "word_scramble": WordScrambleGame,
    "snake": SnakeGame,
}


def build_session_config(
    game: str,
    difficulty: str,
    mode: str = "competitive",
    custom_settings: dict | None = None,
    options: dict | None = None,
) -> SessionConfig:
    if game not in GAME_REGISTRY:
        raise ValueError(f"Unknown game: {game}")
    definition = GAME_REGISTRY[game]
    if difficulty not in definition.difficulties:
        if difficulty == "custom" and "custom_difficulty" in definition.capabilities:
            pass
        else:
            raise ValueError(f"Unsupported custom difficulty for {game}" if difficulty == "custom" else f"Unsupported difficulty for {game}: {difficulty}")
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
    if game not in GAME_REGISTRY:
        raise ValueError(f"Unknown game: {game}")
    definition = GAME_REGISTRY[game]
    print(f"\nConfigure Session: {definition.name}")
    choices = {
        str(number): difficulty
        for number, difficulty in enumerate(definition.difficulties, 1)
    }
    for number, difficulty in choices.items():
        print(f"{number}. {difficulty.title()}")
    difficulty_choice = choose_from_menu(
        "Choose difficulty: ",
        choices,
        input_func=input_func,
    )
    return build_session_config(game, choices[difficulty_choice])


def launch_game(game: str, config: SessionConfig):
    game_instance = GAME_CLASSES[game]()
    state = game_instance.setup(config)
    return game_instance.play(state, config)
def choose_session_mode(*, input_func=input) -> str:
    print("\nSession Mode")
    print("1. Competitive")
    print("2. Practice")
    choice = choose_from_menu(
        "Choose mode: ",
        {"1", "2"},
        input_func=input_func,
    )
    return "competitive" if choice == "1" else "practice"


def choose_game_options(game: str, *, input_func=input) -> dict:
    options = GAME_REGISTRY[game].configuration_options

    if "player_mode" in options:
        print("\nPlayer Mode")
        print("1. Player vs Computer")
        print("2. Player vs Player")
        choice = choose_from_menu(
            "Choose mode: ",
            {"1", "2"},
            input_func=input_func,
        )
        player_mode = "computer" if choice == "1" else "player"

        if "personality" in options and player_mode == "computer":
            print("\nAI Personality")
            print("1. Balanced")
            print("2. Aggressive")
            print("3. Defensive")
            personality_choice = choose_from_menu(
                "Choose personality: ",
                {"1", "2", "3"},
                input_func=input_func,
            )
            personality = {
                "1": "Balanced",
                "2": "Aggressive",
                "3": "Defensive",
            }[personality_choice]
        else:
            personality = "Balanced"

        if "first_player" in options:
            print("\nWho goes first?")
            if player_mode == "computer":
                print("1. Player")
                print("2. Computer")
            else:
                print("1. Player X")
                print("2. Player O")
            first_choice = choose_from_menu(
                "Choose: ",
                {"1", "2"},
                input_func=input_func,
            )
            first_player = (
                "X" if first_choice == "1" else "O"
            )
            return {
                "player_mode": player_mode,
                "first_player": first_player,
            }

        return {
            "player_mode": player_mode,
            "personality": personality,
        }

    if "category" in options:
        game_instance = GAME_CLASSES[game]()
        categories = list(game_instance.words)
        print("\nCategory")
        for number, category in enumerate(categories, 1):
            print(f"{number}. {game_instance.words[category]['name']}")
        choice = choose_from_menu(
            "Choose category: ",
            {str(number) for number in range(1, len(categories) + 1)},
            input_func=input_func,
        )
        return {"category": categories[int(choice) - 1]}

    if "variant" in options:
        print("\nVariant")
        print("1. Standard")
        print("2. Lizard & Spock")
        variant_choice = choose_from_menu(
            "Choose variant: ",
            {"1", "2"},
            input_func=input_func,
        )

        print("\nMatch Type")
        print("1. Single Game")
        print("2. Best of...")
        match_choice = choose_from_menu(
            "Choose: ",
            {"1", "2"},
            input_func=input_func,
        )
        rounds = 1
        if match_choice == "2":
            while True:
                try:
                    rounds = int(input_func("Number of rounds (2-10): ").strip())
                    if 2 <= rounds <= 10:
                        break
                except ValueError:
                    pass
                print("Please choose a number from 2 to 10.")
        return {
            "variant": "standard" if variant_choice == "1" else "extended",
            "match_type": "single" if match_choice == "1" else "match",
            "rounds": rounds,
        }

    if "wrap" in options:
        print("\nWrap-around")
        print("1. Disabled")
        print("2. Enabled")
        choice = choose_from_menu(
            "Choose: ",
            {"1", "2"},
            input_func=input_func,
        )
        return {"wrap": choice == "2"}

    return {}


def main() -> None:
    while True:
        display_game_menu()
        choice = choose_from_menu(
            "Choose an option: ",
            {"1", "2", "3", "4", "5"},
        )
        if choice == "1":
            game = choose_game()
            config = choose_session_config(game)
            options = choose_game_options(game)
            mode = choose_session_mode()
            config = replace(config, mode=mode, options=options)

            while True:
                launch_game(game, config)
                if input("\nRematch this game? (y/n): ").strip().lower() != "y":
                    break

            input("\nPress Enter to return to the hub...")
        elif choice == "2":
            print("\nQuick Play is not available yet.")
            input("Press Enter to return to the hub...")
        elif choice == "3":
            print("\nProfile & Statistics are not available yet.")
            input("Press Enter to return to the hub...")
        elif choice == "4":
            print("\nSettings are not available yet.")
            input("Press Enter to return to the hub...")
        else:
            print("\nThanks for playing.")
            break
if __name__ == "__main__":
    main()