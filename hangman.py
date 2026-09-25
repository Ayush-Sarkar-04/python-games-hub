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
========="""
]
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
def play_game(words):
    category = choose_category(words)
    word = random.choice(words[category]["words"])
    guessed = []
    attempts = 6
    print("\n" + "=" * 40)
    print("              HANGMAN")
    print("=" * 40)
    print("Category:", words[category]["name"])
    while attempts > 0:
        print(HANGMAN_STAGES[6 - attempts])
        print("Category:", words[category]["name"])
        print("Word:    ", display_word(word, guessed))
        print("Mistakes:", 6 - attempts, "/ 6")
        print("Guessed: ", " ".join(sorted(guessed)).upper() if guessed else "None")
        if word_complete(word, guessed):
            print("\n" + "=" * 40)
            print("             YOU WON!")
            print("=" * 40)
            print("You solved:", word.upper())
            print("Mistakes:", 6 - attempts)
            if attempts >= 4:
                print("Perfect guessing!")
            elif attempts >= 2:
                print("Nice work!")
            else:
                print("That was close!")
            return "win"
        guess = input("\nGuess a letter: ").lower().strip()
        if len(guess) != 1 or not guess.isalpha():
            print("Invalid input! Enter ONE letter only.")
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
    print(HANGMAN_STAGES[6])
    print("The word was:", word.upper())
    print("Better luck next time!")
    return "loss"
def main(record_result=None):
    words = get_words()
    print("\n" + "=" * 40)
    print("              HANGMAN")
    print("=" * 40)
    print("       Guess it before it's too late!")
    print("=" * 40)
    while True:
        result = play_game(words)
        if record_result:
            record_result("hangman", result)
        if input("\nPlay again? (y/n): ").lower().strip() != "y":
            print("Thanks for playing Hangman!")
            break
if __name__ == "__main__":
    main()
