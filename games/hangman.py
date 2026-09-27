from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import json
import random
from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import display_title
WORD_SOURCE = "https://gist.githubusercontent.com/johnlindquist/3731fbbbbd3b475f3735cdc61c49a219/raw/categories.json"
HANGMAN_STAGES = [
    """  +---+
  |   |
      |
      |
      |
=========""",
    """  +---+
  |   |
  O   |
      |
      |
=========""",
    """  +---+
  |   |
  O   |
  |   |
      |
=========""",
    """  +---+
  |   |
  O   |
 /|   |
      |
=========""",
    """  +---+
  |   |
  O   |
 /|\\  |
      |
=========""",
    """  +---+
  |   |
  O   |
 /|\\  |
 /    |
=========""",
    """  +---+
  |   |
  O   |
 /|\\  |
 / \\  |
=========""",
]
DIFFICULTIES = {
    "easy": {"name": "Easy", "min_length": 4, "max_length": 6, "attempts": 7},
    "medium": {"name": "Medium", "min_length": 6, "max_length": 8, "attempts": 6},
    "hard": {"name": "Hard", "min_length": 9, "max_length": 99, "attempts": 5},
}
def get_words():
    try:
        with urlopen(WORD_SOURCE, timeout=5) as response:
            return json.loads(response.read().decode())
    except (URLError, HTTPError, TimeoutError, json.JSONDecodeError):
        return {
            "animals": {"name": "Animals", "words": ["Dog", "Lion", "Elephant", "Tiger", "Kangaroo"]},
            "sports": {"name": "Sports", "words": ["Football", "Tennis", "Cricket", "Hockey", "Basketball"]},
        }
def choose_category(words):
    categories = list(words)
    print("\nChoose a category:")
    for number, category in enumerate(categories, 1):
        print(f"{number}. {words[category]['name']}")
    while True:
        choice = input("Choose: ").strip()
        if choice.isdigit() and 1 <= int(choice) <= len(categories):
            return categories[int(choice) - 1]
        print("Invalid choice! Please choose a listed category.")
def display_word(word, guessed):
    return " ".join(letter.upper() if letter in guessed else "_" for letter in word.lower())
def word_complete(word, guessed):
    return all(letter in guessed for letter in word.lower() if letter.isalpha())
class HangmanGame:
    name = "Hangman"
    description = "Guess the hidden word before you run out of attempts"
    def __init__(self, words=None):
        self.words = words or get_words()
        self.win_streak = 0
        self.best_streak = 0
    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "hangman":
            raise ValueError("HangmanGame requires game='hangman'")
        if config.difficulty not in DIFFICULTIES and config.difficulty != "custom":
            raise ValueError(f"Unsupported Hangman difficulty: {config.difficulty}")
        difficulty = DIFFICULTIES.get(config.difficulty)
        attempts = difficulty["attempts"] if difficulty else config.custom_settings.get("attempts", 0)
        if config.difficulty == "custom" and not 3 <= attempts <= 10:
            raise ValueError("Hangman custom attempts must be between 3 and 10")
        category = config.options.get("category") if config.options else None
        if category not in self.words:
            category = choose_category(self.words)
        limits = difficulty or {"min_length": 1, "max_length": 999}
        words = [w for w in self.words[category]["words"] if limits["min_length"] <= len(w) <= limits["max_length"] and w.isalpha()]
        word = random.choice(words or [w for w in self.words[category]["words"] if w.isalpha()])
        return GameState(
            game="hangman",
            data={
                "category": category,
                "word": word.lower(),
                "guessed": set(),
                "attempts": attempts,
                "max_attempts": attempts,
                "hint_used": False,
            },
        )
    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        state.set_status("playing")
        data = state.data
        word = data["word"]
        guessed = data["guessed"]
        category = data["category"]
        display_title("HANGMAN")
        print("Category:", self.words[category]["name"])
        print("Difficulty:", config.difficulty.title())
        print("Hint: Enter H to reveal one letter (once per game).")
        while data["attempts"] > 0:
            mistakes = data["max_attempts"] - data["attempts"]
            print(HANGMAN_STAGES[min(mistakes, len(HANGMAN_STAGES) - 1)])
            print("Category:", self.words[category]["name"])
            print("Word:    ", display_word(word, guessed))
            print("Mistakes:", mistakes, "/", data["max_attempts"])
            print("Guessed: ", " ".join(sorted(guessed)).upper() or "None")
            print("Hint:    ", "Used" if data["hint_used"] else "Available")
            if word_complete(word, guessed):
                return self._finish(state, config, "win")
            guess = input("\nGuess a letter or H for a hint: ").strip().lower()
            if guess == "h":
                if data["hint_used"]:
                    print("You already used your hint this game.")
                    continue
                remaining = list(dict.fromkeys(c for c in word if c.isalpha() and c not in guessed))
                if not remaining:
                    print("There are no letters left to reveal.")
                    continue
                hint = random.choice(remaining)
                guessed.add(hint)
                data["hint_used"] = True
                data["attempts"] -= 1
                state.record_move({"type": "hint", "letter": hint})
                print(f"Hint revealed: {hint.upper()} (-1 attempt)")
                if word_complete(word, guessed):
                    return self._finish(state, config, "win")
                continue
            if len(guess) != 1 or not guess.isalpha():
                print("Invalid input! Enter ONE letter only, or H for a hint.")
                continue
            if guess in guessed:
                print("You already guessed that letter!")
                continue
            guessed.add(guess)
            state.record_move({"type": "guess", "letter": guess})
            if guess in word:
                print("Good guess!")
            else:
                data["attempts"] -= 1
                print("Wrong guess! Keep going." if data["attempts"] else "Wrong guess! That's the last one.")
        return self._finish(state, config, "loss")
    def _finish(self, state, config, outcome):
        data = state.data
        state.set_status(outcome)
        if config.is_competitive:
            if outcome == "win":
                self.win_streak += 1
                self.best_streak = max(self.best_streak, self.win_streak)
            else:
                self.win_streak = 0
        print("\n" + "=" * 40)
        print("YOU WON!" if outcome == "win" else "GAME OVER!")
        print("=" * 40)
        print("The word was:", data["word"].upper())
        return GameResult(
            game="hangman",
            outcome=outcome,
            difficulty=config.difficulty,
            mode=config.mode,
            moves=state.moves,
            metadata={
                "category": data["category"],
                "word_length": len(data["word"]),
                "hint_used": data["hint_used"],
                "mistakes": data["max_attempts"] - data["attempts"],
                "win_streak": self.win_streak,
                "best_streak": self.best_streak,
            },
        )
def main():
    game = HangmanGame()
    print("\n" + "=" * 40 + "\n              HANGMAN\n" + "=" * 40)
    while True:
        print("\nChoose difficulty:\n1. Easy\n2. Medium\n3. Hard")
        difficulty = {"1": "easy", "2": "medium", "3": "hard"}.get(input("Choose: ").strip())
        if not difficulty:
            print("Invalid choice! Please choose 1, 2, or 3.")
            continue
        config = SessionConfig(game="hangman", difficulty=difficulty)
        state = game.setup(config)
        game.play(state, config)
        if input("\nPlay again? (y/n): ").strip().lower() != "y":
            print("Thanks for playing Hangman!")
            break
if __name__ == "__main__":
    main()