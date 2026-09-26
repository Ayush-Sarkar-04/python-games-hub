import json
from pathlib import Path
import connect_four
import hangman
import rock_paper_scissors
import snake
import tic_tac_toe
import word_scramble
GAME_CONFIG = {
    "1": {
        "name": "Tic-Tac-Toe",
        "module": tic_tac_toe,
        "stats": {"played": 0, "wins": 0, "losses": 0, "draws": 0},
        "fields": [("Played", "played"), ("Wins", "wins"), ("Losses", "losses"), ("Draws", "draws")],
    },
    "2": {
        "name": "Hangman",
        "module": hangman,
        "stats": {"played": 0, "wins": 0, "losses": 0},
        "fields": [("Played", "played"), ("Wins", "wins"), ("Losses", "losses")],
    },
    "3": {
        "name": "Rock Paper Scissors",
        "module": rock_paper_scissors,
        "stats": {"played": 0, "wins": 0, "losses": 0, "draws": 0},
        "fields": [("Games/Matches", "played"), ("Wins", "wins"), ("Losses", "losses"), ("Draws", "draws")],
    },
    "4": {
        "name": "Word Scramble",
        "module": word_scramble,
        "stats": {"rounds": 0, "wins": 0, "losses": 0},
        "fields": [("Rounds", "rounds"), ("Wins", "wins"), ("Losses", "losses")],
    },
    "5": {
        "name": "Connect Four",
        "module": connect_four,
        "stats": {"played": 0, "wins": 0, "losses": 0, "draws": 0},
        "fields": [("Played", "played"), ("Wins", "wins"), ("Losses", "losses"), ("Draws", "draws")],
    },
    "6": {
        "name": "Snake",
        "module": snake,
        "stats": {"games": 0, "best_score": 0, "total_score": 0},
        "fields": [("Games", "games"), ("Best Score", "best_score"), ("Total Score", "total_score")],
    },
}
SCOREBOARD_FILE = Path(__file__).with_name("scoreboard.json")
class Scoreboard:
    """Track and persist game results for the Games Hub."""
    def __init__(self, file_path=SCOREBOARD_FILE):
        self.file_path = Path(file_path)
        self.stats = {
            config["name"]: config["stats"].copy()
            for config in GAME_CONFIG.values()
        }
        self.load()
    def load(self):
        """Load saved statistics, keeping defaults for missing or invalid data."""
        if not self.file_path.exists():
            return
        try:
            with self.file_path.open("r", encoding="utf-8") as file:
                saved_stats = json.load(file)
        except (OSError, json.JSONDecodeError):
            return
        if not isinstance(saved_stats, dict):
            return
        for game_name, stats in self.stats.items():
            saved_game_stats = saved_stats.get(game_name)
            if not isinstance(saved_game_stats, dict):
                continue
            for key in stats:
                value = saved_game_stats.get(key)
                if isinstance(value, int) and not isinstance(value, bool) and value >= 0:
                    stats[key] = value
    def save(self):
        """Save current statistics to the local scoreboard file."""
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        temp_file = self.file_path.with_suffix(".tmp")
        try:
            with temp_file.open("w", encoding="utf-8") as file:
                json.dump(self.stats, file, indent=4)
                file.write("\n")
            temp_file.replace(self.file_path)
        except OSError:
            if temp_file.exists():
                temp_file.unlink()
            raise
    def record(self, game, result, score=None):
        """Record one completed game, round, match, or Snake score."""
        game_name = next(
            config["name"]
            for config in GAME_CONFIG.values()
            if config["module"].__name__ == game or config["name"] == game
        )
        stats = self.stats[game_name]
        if game == "snake":
            score = 0 if score is None else score
            stats["games"] += 1
            stats["total_score"] += score
            stats["best_score"] = max(stats["best_score"], score)
            self.save()
            return
        if game == "word_scramble":
            stats["rounds"] += 1
        else:
            stats["played"] += 1
        if result == "win":
            stats["wins"] += 1
        elif result == "loss":
            stats["losses"] += 1
        elif result == "draw" and "draws" in stats:
            stats["draws"] += 1
        self.save()
    def display(self):
        """Display all session statistics."""
        print("\n" + "=" * 52)
        print("                  UNIFIED SCOREBOARD")
        print("=" * 52)
        for config in GAME_CONFIG.values():
            game_name = config["name"]
            stats = self.stats[game_name]
            print(f"\n{game_name}")
            for label, key in config["fields"]:
                print(f"  {label + ':':<15}{stats[key]}")
        print("\n" + "=" * 52)
def display_title():
    print("\n" + "=" * 52)
    print("                 PYTHON GAMES HUB")
    print("=" * 52)
    print("             Choose a game to play")
    print("=" * 52)
def main():
    scoreboard = Scoreboard()
    scoreboard_choice = str(len(GAME_CONFIG) + 1)
    exit_choice = str(len(GAME_CONFIG) + 2)
    while True:
        display_title()
        for choice, config in GAME_CONFIG.items():
            print(f"{choice}. {config['name']}")
        print(f"{scoreboard_choice}. Unified Scoreboard")
        print(f"{exit_choice}. Exit")
        choice = input("\nChoose: ").strip()
        if choice in GAME_CONFIG:
            GAME_CONFIG[choice]["module"].main(scoreboard.record)
        elif choice == scoreboard_choice:
            scoreboard.display()
            input("\nPress Enter to return to the hub...")
        elif choice == exit_choice:
            print("\nThanks for playing!")
            break
        else:
            print(f"\nInvalid choice! Please choose 1-{exit_choice}.")
if __name__ == "__main__":
    main()
