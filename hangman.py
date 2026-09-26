from urllib.request import urlopen
from urllib.error import URLError, HTTPError
import json
import random
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
    "1": {"name": "Easy", "min_length": 4, "max_length": 6, "attempts": 7},
    "2": {"name": "Medium", "min_length": 6, "max_length": 8, "attempts": 6},
    "3": {"name": "Hard", "min_length": 9, "max_length": 99, "attempts": 5},
}
def get_words():
    try:
        response = urlopen(WORD_SOURCE, timeout=5)
        return json.loads(response.read().decode())
    except (URLError, HTTPError, TimeoutError, json.JSONDecodeError):
        return {
            "animals": {
                "name": "Animals",
                "words": ["Dog", "Lion", "Elephant", "Tiger", "Kangaroo"]
            },
            "sports": {
                "name": "Sports",
                "words": ["Football", "Tennis", "Cricket", "Hockey", "Basketball"]
            }
        }
def choose_category(words):
    categories = list(words.keys())
    print("\nChoose a category:")
    for number, category in enumerate(categories, 1):
        print(str(number) + ". " + words[category]["name"])
    while True:
        choice = input("Choose: ").strip()
        try:
            choice = int(choice)
            if 1 <= choice <= len(categories):
                return categories[choice - 1]
        except ValueError:
            pass
        print("Invalid choice! Please choose a listed category.")
def choose_difficulty():
    print("\nChoose difficulty:")
    for key, difficulty in DIFFICULTIES.items():
        print(f"{key}. {difficulty['name']}")
    while True:
        choice = input("Choose: ").strip()
        if choice in DIFFICULTIES:
            return DIFFICULTIES[choice]
        print("Invalid choice! Please choose 1, 2, or 3.")
def choose_word(words, category, difficulty):
    eligible_words = [
        word for word in words[category]["words"]
        if difficulty["min_length"] <= len(word) <= difficulty["max_length"]
        and word.isalpha()
    ]
    if not eligible_words:
        eligible_words = [
            word for word in words[category]["words"]
            if word.isalpha()
        ]

    return random.choice(eligible_words)
def display_word(word, guessed):
    display = ""
    for letter in word.lower():
        if not letter.isalpha():
            display += letter + " "
        elif letter in guessed:
            display += letter.upper() + " "
        else:
            display += "_ "
    return display
def word_complete(word, guessed):
    for letter in word.lower():
        if letter.isalpha() and letter not in guessed:
            return False
    return True
def use_hint(word, guessed):
    remaining = [
        letter for letter in dict.fromkeys(word.lower())
        if letter.isalpha() and letter not in guessed
    ]
    if not remaining:
        return None
    hint = random.choice(remaining)
    guessed.append(hint)
    return hint
def display_streak(streak):
    print(f"Session win streak: {streak}")
def play_game(words, streak=0):
    category = choose_category(words)
    difficulty = choose_difficulty()
    word = choose_word(words, category, difficulty)
    guessed = []
    attempts = difficulty["attempts"]
    max_attempts = attempts
    hint_used = False
    print("\n" + "=" * 40)
    print("              HANGMAN")
    print("=" * 40)
    print("Category:", words[category]["name"])
    print("Difficulty:", difficulty["name"])
    print("Hint: Enter H to reveal one letter (once per game).")
    display_streak(streak)
    while attempts > 0:
        mistakes = max_attempts - attempts
        stage = min(mistakes, len(HANGMAN_STAGES) - 1)
        print(HANGMAN_STAGES[stage])
        print("Category:", words[category]["name"])
        print("Difficulty:", difficulty["name"])
        print("Word:    ", display_word(word, guessed))
        print("Mistakes:", mistakes, "/", max_attempts)
        print("Guessed: ", " ".join(sorted(guessed)).upper() if guessed else "None")
        print("Hint:    ", "Available" if not hint_used else "Used")
        if word_complete(word, guessed):
            print("\n" + "=" * 40)
            print("             YOU WON!")
            print("=" * 40)
            print("You solved:", word.upper())
            print("Mistakes:", mistakes)
            if streak + 1 > 1:
                print(f"Win streak: {streak + 1}")
            else:
                print("Win streak: 1")
            if mistakes <= 1:
                print("Perfect guessing!")
            elif mistakes <= 2:
                print("Nice work!")
            else:
                print("That was close!")
            return "win"
        guess = input("\nGuess a letter or H for a hint: ").lower().strip()
        if guess == "h":
            if hint_used:
                print("You already used your hint this game.")
                continue
            hint = use_hint(word, guessed)
            if hint is None:
                print("There are no letters left to reveal.")
                continue
            hint_used = True
            attempts -= 1
            print(f"Hint revealed: {hint.upper()} (-1 attempt)")
            if attempts == 0:
                print("The hint used your last attempt.")
            continue
        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input! Enter ONE letter only, or H for a hint.")
            continue
        if guess in guessed:
            print("You already guessed that letter!")
            continue
        guessed.append(guess)
        if guess in word.lower():
            remaining = sum(
                1 for letter in word.lower()
                if letter.isalpha() and letter not in guessed
            )
            if remaining == 0:
                print("That's it! You found the last letter!")
            elif remaining <= 2:
                print("Great guess! You're very close!")
            else:
                print("Good guess!")
        else:
            attempts -= 1
            if attempts == 0:
                print("Wrong guess! That's the last one.")
            elif attempts == 1:
                print("Wrong guess! One mistake left.")
            else:
                print("Wrong guess! Keep going.")
    print("\n" + "=" * 40)
    print("            GAME OVER!")
    print("=" * 40)
    print(HANGMAN_STAGES[-1])
    print("The word was:", word.upper())
    print("Your win streak has reset.")
    return "loss"
def main(record_result=None):
    words = get_words()
    streak = 0
    print("\n" + "=" * 40)
    print("              HANGMAN")
    print("=" * 40)
    print("       Guess it before it's too late!")
    print("=" * 40)
    while True:
        result = play_game(words, streak)
        if record_result:
            record_result("hangman", result)
        if result == "win":
            streak += 1
        else:
            streak = 0
        if input("\nPlay again? (y/n): ").lower().strip() != "y":
            print("Thanks for playing Hangman!")
            break
if __name__ == "__main__":
    main()
