"""Python Games Hub: session configuration, gameplay, and progression integration."""

import random
from dataclasses import dataclass
from pathlib import Path

from engine.achievements import AchievementStore, ALL_ACHIEVEMENT_DEFINITIONS, unlock_achievements
from engine.game import SessionConfig
from engine.profiles import ProfileStore, update_profile
from engine.settings import SettingsStore, VALID_BANNER_STYLES
from engine.statistics import StatisticsStore, suggest_difficulty, update_statistics
from engine.utils import choose_from_menu, display_title
from games.tic_tac_toe import TicTacToeGame
from games.connect_four import ConnectFourGame
from games.hangman import HangmanGame
from games.rock_paper_scissors import RockPaperScissorsGame
from games.word_scramble import WordScrambleGame
from games.snake import SnakeGame
from games.minesweeper import MinesweeperGame
from games.typing_test import TypingTestGame
from games.mastermind import MastermindGame


DATA_DIR = Path(".game_data")
EXPORT_PATH = Path("player_summary.md")


@dataclass(frozen=True)
class GameDefinition:
    name: str
    description: str
    game_class: type
    capabilities: frozenset[str]
    modes: frozenset[str]
    difficulties: tuple[str, ...]
    configuration_options: frozenset[str] = frozenset()
    custom_parameters: tuple[tuple[str, int, int, str], ...] = ()


GAME_REGISTRY = {
    "tic_tac_toe": GameDefinition(
        "Tic-Tac-Toe", "Classic 3x3 strategy game",
        TicTacToeGame,
        frozenset({"replay", "history", "hint", "practice", "custom_difficulty"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
        frozenset({"player_mode", "personality"}),
        tuple((key, *values) for key, values in TicTacToeGame.CUSTOM_PARAMETERS.items()),
    ),
    "hangman": GameDefinition(
        "Hangman", "Guess the hidden word before you run out of attempts",
        HangmanGame,
        frozenset({"hint", "practice", "custom_difficulty"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
        frozenset({"category"}),
        tuple((key, *values) for key, values in HangmanGame.CUSTOM_PARAMETERS.items()),
    ),
    "rock_paper_scissors": GameDefinition(
        "Rock Paper Scissors", "Classic RPS with optional Lizard & Spock",
        RockPaperScissorsGame,
        frozenset({"history", "practice"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
        frozenset({"variant", "match_type", "rounds"}),
    ),
    "word_scramble": GameDefinition(
        "Word Scramble", "Unscramble words across multiple difficulty levels",
        WordScrambleGame,
        frozenset({"hint", "practice"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
    ),
    "connect_four": GameDefinition(
        "Connect Four", "Connect four pieces before your opponent",
        ConnectFourGame,
        frozenset({"replay", "history", "hint", "practice", "custom_difficulty"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
        frozenset({"player_mode", "first_player"}),
        tuple((key, *values) for key, values in ConnectFourGame.CUSTOM_PARAMETERS.items()),
    ),
    "snake": GameDefinition(
        "Snake", "Classic terminal Snake with score-based play",
        SnakeGame,
        frozenset({"run_history", "practice"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
        frozenset({"wrap"}),
    ),
    "minesweeper": GameDefinition(
        "Minesweeper", "Reveal safe cells, flag mines, and clear the board",
        MinesweeperGame,
        frozenset({"practice"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
    ),
    "typing_test": GameDefinition(
        "Typing Test", "Measure typing speed and accuracy",
        TypingTestGame,
        frozenset({"practice"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
    ),
    "mastermind": GameDefinition(
        "Mastermind", "Crack the hidden color code",
        MastermindGame,
        frozenset({"practice"}),
        frozenset({"competitive", "practice"}), ("easy", "medium", "hard"),
    ),
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
            settings = definition.game_class.validate_custom_settings(custom_settings or {})
        else:
            message = (
                f"Unsupported custom difficulty for {game}"
                if difficulty == "custom"
                else f"Unsupported difficulty for {game}: {difficulty}"
            )
            raise ValueError(message)
    else:
        settings = {}
    if mode not in definition.modes:
        raise ValueError(f"Unsupported mode for {game}: {mode}")
    return SessionConfig(
        game=game,
        difficulty=difficulty,
        mode=mode,
        custom_settings=settings,
        options=options or {},
    )


def display_game_menu(style="default") -> None:
    display_title("PYTHON GAMES HUB", style=style)
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


def choose_session_config(
    game: str,
    *,
    input_func=input,
    statistics=None,
) -> SessionConfig:
    if game not in GAME_REGISTRY:
        raise ValueError(f"Unknown game: {game}")
    definition = GAME_REGISTRY[game]
    print(f"\nConfigure Session: {definition.name}")

    if statistics:
        suggestion = suggest_difficulty(game, statistics)
        if suggestion:
            print(f"Suggested difficulty: {suggestion.title()} (advisory only)")

    choices = {str(number): difficulty for number, difficulty in enumerate(definition.difficulties, 1)}
    for number, difficulty in choices.items():
        print(f"{number}. {difficulty.title()}")

    advanced_number = None
    if "custom_difficulty" in definition.capabilities:
        advanced_number = str(len(choices) + 1)
        print(f"{advanced_number}. Advanced / Custom")

    valid_choices = set(choices)
    if advanced_number:
        valid_choices.add(advanced_number)

    difficulty_choice = choose_from_menu(
        "Choose difficulty: ",
        valid_choices,
        input_func=input_func,
    )
    if difficulty_choice == advanced_number:
        custom_settings = choose_custom_settings(definition, input_func=input_func)
        return build_session_config(game, "custom", custom_settings=custom_settings)
    return build_session_config(game, choices[difficulty_choice])


def choose_custom_settings(definition: GameDefinition, *, input_func=input) -> dict:
    print(f"\n{definition.name.upper()} — CUSTOM")
    values = {}
    for key, minimum, maximum, label in definition.custom_parameters:
        while True:
            raw = input_func(f"{label} ({minimum}-{maximum}): ").strip()
            try:
                value = int(raw)
                candidate = dict(values)
                candidate[key] = value
                values = definition.game_class.validate_custom_settings(candidate)
                break
            except (TypeError, ValueError) as exc:
                print(exc)
    return values


def launch_game(game: str, config: SessionConfig):
    if game not in GAME_REGISTRY:
        raise ValueError(f"Unknown game: {game}")
    game_instance = GAME_REGISTRY[game].game_class()
    state = game_instance.setup(config)
    return game_instance.play(state, config)


def choose_session_mode(*, input_func=input) -> str:
    print("\nSession Mode")
    print("1. Competitive")
    print("2. Practice")
    choice = choose_from_menu("Choose mode: ", {"1", "2"}, input_func=input_func)
    return "competitive" if choice == "1" else "practice"


def choose_game_options(game: str, *, input_func=input) -> dict:
    options = GAME_REGISTRY[game].configuration_options

    if "player_mode" in options:
        print("\nPlayer Mode")
        print("1. Player vs Computer")
        print("2. Player vs Player")
        choice = choose_from_menu("Choose mode: ", {"1", "2"}, input_func=input_func)
        player_mode = "computer" if choice == "1" else "player"

        personality = "Balanced"
        if "personality" in options and player_mode == "computer":
            print("\nAI Personality")
            print("1. Balanced")
            print("2. Aggressive")
            print("3. Defensive")
            personality = {
                "1": "Balanced",
                "2": "Aggressive",
                "3": "Defensive",
            }[choose_from_menu("Choose personality: ", {"1", "2", "3"}, input_func=input_func)]

        if "first_player" in options:
            print("\nWho goes first?")
            if player_mode == "computer":
                print("1. Player")
                print("2. Computer")
            else:
                print("1. Player X")
                print("2. Player O")
            first_choice = choose_from_menu("Choose: ", {"1", "2"}, input_func=input_func)
            return {
                "player_mode": player_mode,
                "first_player": "X" if first_choice == "1" else "O",
            }

        return {"player_mode": player_mode, "personality": personality}

    if "category" in options:
        game_instance = GAME_REGISTRY[game].game_class()
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
        variant_choice = choose_from_menu("Choose: ", {"1", "2"}, input_func=input_func)

        print("\nMatch Type")
        print("1. Single Game")
        print("2. Fixed-Length Match")
        match_choice = choose_from_menu("Choose: ", {"1", "2"}, input_func=input_func)
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
        choice = choose_from_menu("Choose: ", {"1", "2"}, input_func=input_func)
        return {"wrap": choice == "2"}

    return {}


def default_game_options(game: str) -> dict:
    definition = GAME_REGISTRY[game]
    options = definition.configuration_options
    if "player_mode" in options:
        result = {"player_mode": "computer"}
        if "personality" in options:
            result["personality"] = "Balanced"
        if "first_player" in options:
            result["first_player"] = "X"
        return result
    if "category" in options:
        game_instance = definition.game_class()
        return {"category": next(iter(game_instance.words))}
    if "variant" in options:
        return {"variant": "standard", "match_type": "single", "rounds": 1}
    if "wrap" in options:
        return {"wrap": False}
    return {}


def process_result(
    result,
    *,
    profile_store=None,
    statistics_store=None,
    achievement_store=None,
):
    profile_store = profile_store or ProfileStore(DATA_DIR / "profile.json")
    statistics_store = statistics_store or StatisticsStore(DATA_DIR / "statistics.json")
    achievement_store = achievement_store or AchievementStore(DATA_DIR / "achievements.json")

    statistics = update_statistics(statistics_store.load(), result)
    statistics_store.save(statistics)

    profile = profile_store.load()
    profile, new_style = update_profile(profile, result)
    profile_store.save(profile)

    earned = unlock_achievements(achievement_store, result, statistics)
    return {
        "statistics": statistics,
        "profile": profile,
        "achievements": earned,
        "new_style": new_style,
    }


def display_profile(profile) -> None:
    print("\nPROFILE")
    print("=" * 48)
    print(f"Name            : {profile.name}")
    print(f"Level           : {profile.level}")
    print(f"XP              : {profile.xp}")
    print(f"Unlocked styles : {', '.join(profile.unlocked_styles)}")


def display_statistics(statistics) -> None:
    print("\nSTATISTICS")
    print("=" * 48)
    if not statistics:
        print("No competitive statistics yet.")
        return
    for game, stats in statistics.items():
        print(f"\n{game.replace('_', ' ').title()}")
        for key, value in stats.items():
            if key == "recent_results":
                continue
            print(f"  {key.replace('_', ' ').title()}: {value}")


def display_achievements(records) -> None:
    print("\nACHIEVEMENTS")
    print("=" * 48)
    for definition in ALL_ACHIEVEMENT_DEFINITIONS:
        record = records.get(definition.id, {})
        status = "UNLOCKED" if record.get("unlocked") else "Locked"
        print(f"{status:10} {definition.name} — {definition.description}")


def export_summary(profile, statistics, achievements, path=EXPORT_PATH) -> Path:
    lines = [
        "# Python Games Hub — Player Summary",
        "",
        "## Profile",
        "",
        f"- **Name:** {profile.name}",
        f"- **Level:** {profile.level}",
        f"- **XP:** {profile.xp}",
        f"- **Unlocked styles:** {', '.join(profile.unlocked_styles)}",
        "",
        "## Statistics",
        "",
    ]
    if statistics:
        for game, stats in statistics.items():
            lines.append(f"### {game.replace('_', ' ').title()}")
            for key, value in stats.items():
                if key != "recent_results":
                    lines.append(f"- **{key.replace('_', ' ').title()}:** {value}")
            lines.append("")
    else:
        lines.append("No competitive statistics yet.")
        lines.append("")

    lines.extend(["## Achievements", ""])
    for definition in ALL_ACHIEVEMENT_DEFINITIONS:
        record = achievements.get(definition.id, {})
        status = "Unlocked" if record.get("unlocked") else "Locked"
        lines.append(f"- **{definition.name}:** {status} — {definition.description}")
    path = Path(path)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    return path


def profile_statistics_menu(*, input_func=input, base_dir=DATA_DIR, export_path=EXPORT_PATH):
    profile_store = ProfileStore(Path(base_dir) / "profile.json")
    statistics_store = StatisticsStore(Path(base_dir) / "statistics.json")
    achievement_store = AchievementStore(Path(base_dir) / "achievements.json")
    while True:
        print("\nPROFILE & STATISTICS")
        print("1. View Profile")
        print("2. View Statistics")
        print("3. View Achievements")
        print("4. Export Summary")
        print("5. Back")
        choice = choose_from_menu("Choose: ", {"1", "2", "3", "4", "5"}, input_func=input_func)
        if choice == "1":
            display_profile(profile_store.load())
        elif choice == "2":
            display_statistics(statistics_store.load())
        elif choice == "3":
            display_achievements(achievement_store.load())
        elif choice == "4":
            path = export_summary(
                profile_store.load(),
                statistics_store.load(),
                achievement_store.load(),
                export_path,
            )
            print(f"Summary exported to {path}")
        else:
            break


def settings_menu(settings_store: SettingsStore, profile=None, *, input_func=input) -> dict:
    settings = settings_store.load()
    available_styles = tuple(profile.unlocked_styles) if profile else ("default",)
    while True:
        print("\nSETTINGS")
        print("1. Banner Style")
        print(f"2. Auto-Suggest Difficulty: {'On' if settings['auto_suggest_difficulty'] else 'Off'}")
        print("3. Back")
        choice = choose_from_menu("Choose: ", {"1", "2", "3"}, input_func=input_func)
        if choice == "1":
            styles = sorted(set(available_styles) & VALID_BANNER_STYLES) or ["default"]
            print("\nBanner Style")
            for number, style in enumerate(styles, 1):
                print(f"{number}. {style.title()}")
            selected = choose_from_menu(
                "Choose: ",
                {str(number) for number in range(1, len(styles) + 1)},
                input_func=input_func,
            )
            settings["banner_style"] = styles[int(selected) - 1]
            settings_store.save(settings)
        elif choice == "2":
            settings["auto_suggest_difficulty"] = not settings["auto_suggest_difficulty"]
            settings_store.save(settings)
        else:
            return settings


def quick_play(*, statistics=None):
    game = random.choice(list(GAME_REGISTRY))
    difficulty = suggest_difficulty(game, statistics or {}) or "medium"
    config = build_session_config(
        game,
        difficulty,
        mode="competitive",
        options=default_game_options(game),
    )
    print(f"\nQuick Play: {GAME_REGISTRY[game].name} — {difficulty.title()}")
    return launch_game(game, config)


def main() -> None:
    settings_store = SettingsStore(DATA_DIR / "settings.json")
    profile_store = ProfileStore(DATA_DIR / "profile.json")
    settings = settings_store.load()
    profile = profile_store.load()
    if settings["banner_style"] not in profile.unlocked_styles:
        settings["banner_style"] = "default"
        settings_store.save(settings)
    while True:
        display_game_menu(settings["banner_style"])
        choice = choose_from_menu("Choose an option: ", {"1", "2", "3", "4", "5"})
        if choice == "1":
            game = choose_game()
            statistics = StatisticsStore(DATA_DIR / "statistics.json").load()
            config = choose_session_config(
                game,
                statistics=statistics if settings["auto_suggest_difficulty"] else None,
            )
            options = choose_game_options(game)
            mode = choose_session_mode()
            config = SessionConfig(
                game=config.game,
                difficulty=config.difficulty,
                mode=mode,
                custom_settings=config.custom_settings,
                options=options,
            )
            while True:
                result = launch_game(game, config)
                processed = process_result(result)
                for achievement_id in processed["achievements"]:
                    print(f"Achievement unlocked: {achievement_id}")
                if processed["new_style"]:
                    print(f"New banner style unlocked: {processed['new_style']}")
                if input("\nRematch this game? (y/n): ").strip().lower() != "y":
                    break
            input("\nPress Enter to return to the hub...")
        elif choice == "2":
            result = quick_play(
                statistics=StatisticsStore(DATA_DIR / "statistics.json").load()
            )
            process_result(result)
            input("\nPress Enter to return to the hub...")
        elif choice == "3":
            profile_statistics_menu()
        elif choice == "4":
            profile = ProfileStore(DATA_DIR / "profile.json").load()
            settings = settings_menu(settings_store, profile)
        else:
            print("\nThanks for playing.")
            break


if __name__ == "__main__":
    main()
