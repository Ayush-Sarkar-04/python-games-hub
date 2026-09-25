import json
import random
from urllib.request import urlopen
from urllib.error import URLError, HTTPError
from urllib.parse import urlencode
WORD_API = "https://random-word-api.herokuapp.com/word"
FALLBACK_WORDS = {
    "1": ["apple", "table", "house", "water", "happy", "green"],
    "2": ["journey", "computer", "football", "library", "diamond", "weather"],
    "3": ["adventure", "knowledge", "algorithm", "butterfly", "challenge", "important"]
}
DIFFICULTY = {
    "1": ("Easy", 4, 6),
    "2": ("Medium", 6, 8),
    "3": ("Hard", 8, 10)
}
MAX_ATTEMPTS = 3
def display_title():
    print("\n" + "=" * 48)
    print("              WORD SCRAMBLE")
    print("=" * 48)
    print("            Unscramble. Guess. Win.")
    print("=" * 48)
def choose_difficulty():
    while True:
        print("\n" + "-" * 48)
        print("                 DIFFICULTY")
        print("-" * 48)
        print("  1. Easy")
        print("  2. Medium")
        print("  3. Hard")
        print("  4. Exit")
        choice = input("\nChoose: ").strip()
        if choice in DIFFICULTY:
            return choice
        if choice == "4":
            return None
        print("Invalid choice! Please choose 1, 2, 3, or 4.")
def get_word(difficulty):
    _, min_length, max_length = DIFFICULTY[difficulty]
    params = {
        "number": 1,
        "minLength": min_length,
        "maxLength": max_length,
    }
    url = f"{WORD_API}?{urlencode(params)}"
    try:
        with urlopen(url, timeout=5) as response:
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
    while True:
        random.shuffle(letters)
        scrambled = "".join(letters)
        if scrambled != word:
            return scrambled
def get_guess():
    while True:
        guess = input("\nYour guess: ").strip().lower()
        if not guess:
            print("Please enter a word.")
            continue
        if not guess.isalpha():
            print("Please use letters only.")
            continue
        return guess
def display_attempts(attempts_used):
    remaining = MAX_ATTEMPTS - attempts_used
    markers = "● " * attempts_used + "○ " * remaining
    print(f"Attempts: {markers.strip()}")
def display_round_header(difficulty, scrambled, round_number):
    difficulty_name = DIFFICULTY[difficulty][0]
    print("\n" + "=" * 48)
    print(f"                    ROUND {round_number}")
    print("=" * 48)
    print(f"Difficulty : {difficulty_name}")
    print(f"Word length: {len(scrambled)}")
    print()
    print("             " + "  ".join(scrambled.upper()))
    print("=" * 48)
HINT_SCHEDULE = {
    "1": {"after_first_miss": 1, "on_last_try": 2},
    "2": {"after_first_miss": 1, "on_last_try": 1},
    "3": {"after_first_miss": 0, "on_last_try": 1},
}
def reveal_more_letters(word, revealed_indices, count):
    available = [i for i in range(len(word)) if i not in revealed_indices]
    count = min(count, len(available))
    revealed_indices.update(random.sample(available, count))
def render_hint(word, revealed_indices):
    return "  ".join(
        letter.upper() if i in revealed_indices else "_"
        for i, letter in enumerate(word)
    )
def display_result(won, word, attempts_used):
    print("\n" + "=" * 48)
    if won:
        print("                 CORRECT!")
        print("=" * 48)
        if attempts_used == 1:
            print("          Perfect first-try solve!")
        elif attempts_used == MAX_ATTEMPTS:
            print("          That was close!")
        else:
            print("             Nice work!")
    else:
        print("                GAME OVER")
        print("=" * 48)
        print("             Out of attempts!")
    print(f"\nThe word was: {word.upper()}")
    print("=" * 48)
def play_round(difficulty, round_number):
    word = get_word(difficulty)
    scrambled = scramble_word(word)
    attempts_used = 0
    revealed_indices = set()
    schedule = HINT_SCHEDULE[difficulty]
    display_round_header(difficulty, scrambled, round_number)
    while attempts_used < MAX_ATTEMPTS:
        display_attempts(attempts_used)
        guess = get_guess()
        attempts_used += 1
        if guess == word:
            display_result(True, word, attempts_used)
            return "win"
        remaining = MAX_ATTEMPTS - attempts_used
        if remaining:
            if attempts_used == 1 and schedule["after_first_miss"]:
                reveal_more_letters(word, revealed_indices, schedule["after_first_miss"])
            if remaining == 1:
                reveal_more_letters(word, revealed_indices, schedule["on_last_try"])
            if revealed_indices:
                print(f"\nHint: {render_hint(word, revealed_indices)}")
            if remaining == 1:
                print("Very close! One attempt left.")
            else:
                print("Not quite! Give it another shot.")
    display_result(False, word, attempts_used)
    return "loss"
def play_again():
    while True:
        choice = input("\nPlay again? (y/n): ").strip().lower()
        if choice in ("y", "n"):
            return choice == "y"
        print("Invalid input! Enter y or n.")
def main(record_result=None):
    score = 0
    rounds = 0
    while True:
        display_title()
        difficulty = choose_difficulty()
        if difficulty is None:
            print("\nThanks for playing Word Scramble!")
            break
        rounds += 1
        result = play_round(difficulty, rounds)
        if result == "win":
            score += 1
        if record_result:
            record_result("word_scramble", result)
        print("\n" + "-" * 48)
        print("                 SCOREBOARD")
        print("-" * 48)
        print(f"                 Wins: {score}")
        print(f"                 Rounds: {rounds}")
        print(f"                 Success: {score}/{rounds}")
        print("-" * 48)
        if not play_again():
            print("\n" + "=" * 48)
            print("              FINAL SCORE")
            print("=" * 48)
            print(f"              {score} / {rounds}")
            print("=" * 48)
            print("\nThanks for playing Word Scramble!")
            break
if __name__ == "__main__":
    main()