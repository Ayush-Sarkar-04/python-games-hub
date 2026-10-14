import json
import random
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import display_title
WORD_API = "https://random-word-api.herokuapp.com/word"
FALLBACK_WORDS = {
    "easy": ["apple", "table", "house", "water", "happy", "green"],
    "medium": ["journey", "computer", "football", "library", "diamond", "weather"],
    "hard": ["adventure", "knowledge", "algorithm", "butterfly", "challenge", "important"],
}
DIFFICULTY = {
    "easy": ("Easy", 4, 6),
    "medium": ("Medium", 6, 8),
    "hard": ("Hard", 8, 10),
}
MAX_ATTEMPTS = 3
SCORE_BY_ATTEMPT = {1: 3, 2: 2, 3: 1}
HINT_SCHEDULE = {
    "easy": (1, 1),
    "medium": (0, 1),
    "hard": (0, 0),
}
def get_word(difficulty):
    _, min_length, max_length = DIFFICULTY[difficulty]
    params = urlencode({"number": 1, "minLength": min_length, "maxLength": max_length})
    try:
        with urlopen(f"{WORD_API}?{params}", timeout=5) as response:
            data = json.loads(response.read().decode("utf-8"))
        if data and isinstance(data[0], str):
            word = data[0].lower()
            if word.isalpha() and min_length <= len(word) <= max_length:
                return word
    except (HTTPError, URLError, TimeoutError, OSError, ValueError, IndexError):
        pass
    return random.choice(FALLBACK_WORDS[difficulty])
def scramble_word(word):
    letters = list(word)
    if len(set(letters)) <= 1:
        return word
    while True:
        random.shuffle(letters)
        scrambled = "".join(letters)
        if scrambled != word:
            return scrambled
def get_guess():
    while True:
        guess = input("\nYour guess: ").strip().lower()
        if guess.isalpha():
            return guess
        print("Please enter letters only.")
def reveal_more_letters(word, revealed, count):
    available = [i for i in range(len(word)) if i not in revealed]
    revealed.update(random.sample(available, min(count, len(available))))
def render_hint(word, revealed):
    return "  ".join(
        letter.upper() if index in revealed else "_"
        for index, letter in enumerate(word)
    )
def display_result(won, word, attempts):
    print("\n" + "=" * 48)
    print("                 CORRECT!" if won else "                GAME OVER")
    print("=" * 48)
    if won:
        messages = {
            1: "          Perfect first-try solve!",
            2: "             Nice work!",
            3: "          That was close!",
        }
        print(messages[attempts])
    else:
        print("             Out of attempts!")
    print(f"\nThe word was: {word.upper()}")
    print("=" * 48)
class WordScrambleGame:
    name = "Word Scramble"
    description = "Unscramble a word before you run out of attempts"
    def __init__(self):
        self.win_streak = 0
        self.best_streak = 0
        self.total_score = 0
        self.rounds = 0
    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "word_scramble":
            raise ValueError("WordScrambleGame requires game='word_scramble'")
        if config.difficulty not in DIFFICULTY:
            raise ValueError(f"Unsupported Word Scramble difficulty: {config.difficulty}")
        word = get_word(config.difficulty)
        return GameState(
            game="word_scramble",
            data={
                "word": word,
                "scrambled": scramble_word(word),
                "attempts": 0,
                "revealed": set(),
                "score": 0,
            },
        )
    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        state.set_status("playing")
        self.rounds += 1
        data = state.data
        word = data["word"]
        first_hint, last_hint = HINT_SCHEDULE[config.difficulty]
        display_title("WORD SCRAMBLE")
        print(f"Difficulty : {DIFFICULTY[config.difficulty][0]}")
        print(f"Word length: {len(word)}")
        print("\n             " + "  ".join(data["scrambled"].upper()))
        print("=" * 48)
        while data["attempts"] < MAX_ATTEMPTS:
            remaining = MAX_ATTEMPTS - data["attempts"]
            print(f"\nAttempts: {'● ' * data['attempts'] + '○ ' * remaining}".strip())
            guess = get_guess()
            data["attempts"] += 1
            state.record_move({"guess": guess, "attempt": data["attempts"]})
            if guess == word:
                data["score"] = SCORE_BY_ATTEMPT[data["attempts"]]
                return self._finish(state, config, "win")
            remaining = MAX_ATTEMPTS - data["attempts"]
            if remaining:
                if data["attempts"] == 1:
                    reveal_more_letters(word, data["revealed"], first_hint)
                if remaining == 1:
                    reveal_more_letters(word, data["revealed"], last_hint)
                if data["revealed"]:
                    print(f"\nHint: {render_hint(word, data['revealed'])}")
                print("Very close! One attempt left." if remaining == 1
                      else "Not quite! Give it another shot.")
        return self._finish(state, config, "loss")
    def _finish(self, state, config, outcome):
        data = state.data
        state.set_status(outcome)
        score = data["score"]
        if config.is_competitive:
            if outcome == "win":
                self.win_streak += 1
                self.best_streak = max(self.best_streak, self.win_streak)
                self.total_score += score
            else:
                self.win_streak = 0
        display_result(outcome == "win", data["word"], data["attempts"])
        return GameResult(
            game="word_scramble",
            outcome=outcome,
            difficulty=config.difficulty,
            mode=config.mode,
            score=score,
            moves=state.moves,
            metadata={
                "attempts": data["attempts"],
                "word_length": len(data["word"]),
                "win_streak": self.win_streak,
                "best_streak": self.best_streak,
                "total_score": self.total_score,
            },
        )
def main():
    game = WordScrambleGame()
    while True:
        display_title("WORD SCRAMBLE")
        print("\n1. Easy\n2. Medium\n3. Hard\n4. Exit")
        difficulty = {
            "1": "easy",
            "2": "medium",
            "3": "hard",
        }.get(input("\nChoose: ").strip())
        if not difficulty:
            if input_choice := input("\nExit? (y/n): ").strip().lower() == "y":
                print("\nThanks for playing Word Scramble!")
                break
            continue
        config = SessionConfig(game="word_scramble", difficulty=difficulty)
        game.play(game.setup(config), config)
        if input("\nPlay again? (y/n): ").strip().lower() != "y":
            print("\nThanks for playing Word Scramble!")
            break
if __name__ == "__main__":
    main()