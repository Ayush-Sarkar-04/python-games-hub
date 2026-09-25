import random
CHOICES = {
    "1": "rock",
    "2": "paper",
    "3": "scissors"
}
MOVES = list(CHOICES.values())
def display_title():
    print("\n" + "=" * 42)
    print("          ROCK PAPER SCISSORS")
    print("=" * 42)
def display_choices():
    print("\nChoose your move:")
    print("  1. Rock")
    print("  2. Paper")
    print("  3. Scissors")
def get_player_choice():
    while True:
        display_choices()
        choice = input("\nYour choice: ").strip()
        if choice in CHOICES:
            return CHOICES[choice]
        print("\nInvalid choice! Please choose 1, 2, or 3.")
def get_round_winner(player, computer):
    if player == computer:
        return "draw"
    if (
        (player == "rock" and computer == "scissors")
        or (player == "paper" and computer == "rock")
        or (player == "scissors" and computer == "paper")
    ):
        return "player"
    return "computer"
def display_round_result(player, computer, result):
    print("\n" + "-" * 42)
    print(f"You      : {player.title()}")
    print(f"Computer : {computer.title()}")
    print("-" * 42)
    if result == "player":
        print("Result   : YOU WIN!")
    elif result == "computer":
        print("Result   : COMPUTER WINS!")
    else:
        print("Result   : DRAW!")
def display_score(player_score, computer_score):
    print(
        f"\nScore    : You {player_score}  |  "
        f"Computer {computer_score}"
    )
def play_round():
    player = get_player_choice()
    computer = random.choice(MOVES)
    result = get_round_winner(player, computer)
    display_round_result(player, computer, result)
    return result


def play_single_game():
    print("\n" + "-" * 42)
    print("                 SINGLE GAME")
    print("-" * 42)
    result = play_round()
    return {"player": "win", "computer": "loss", "draw": "draw"}[result]
def get_match_length():
    while True:
        choice = input("\nNumber of rounds (2-10): ").strip()
        try:
            rounds = int(choice)
        except ValueError:
            print("Invalid input! Enter a number from 2 to 10.")
            continue
        if 2 <= rounds <= 10:
            return rounds
        print("Please choose a number from 2 to 10.")
def play_match():
    print("\n" + "-" * 42)
    print("                 BEST OF...")
    print("-" * 42)
    total_rounds = get_match_length()
    player_score = 0
    computer_score = 0
    for round_number in range(1, total_rounds + 1):
        print("\n" + "=" * 42)
        print(f"                 ROUND {round_number}/{total_rounds}")
        print("=" * 42)
        player = get_player_choice()
        computer = random.choice(MOVES)
        result = get_round_winner(player, computer)
        display_round_result(player, computer, result)
        if result == "player":
            player_score += 1
        elif result == "computer":
            computer_score += 1
        display_score(player_score, computer_score)
    print("\n" + "=" * 42)
    print("                  MATCH RESULT")
    print("=" * 42)
    if player_score > computer_score:
        print(f"YOU WIN THE MATCH!  {player_score} - {computer_score}")
        match_result = "win"
    elif computer_score > player_score:
        print(f"COMPUTER WINS!      {computer_score} - {player_score}")
        match_result = "loss"
    else:
        print(f"MATCH DRAW!         {player_score} - {computer_score}")
        match_result = "draw"
    print("=" * 42)
    return match_result
def play_again():
    while True:
        choice = input("\nPlay again? (y/n): ").strip().lower()
        if choice in ("y", "n"):
            return choice == "y"
        print("Invalid input! Enter y or n.")
def main(record_result=None):
    while True:
        display_title()
        print("\n1. Single Game")
        print("2. Best of...")
        print("3. Exit")
        choice = input("\nChoose: ").strip()
        if choice == "1":
            result = play_single_game()
            if record_result:
                record_result("rock_paper_scissors", result)
        elif choice == "2":
            result = play_match()
            if record_result:
                record_result("rock_paper_scissors", result)
        elif choice == "3":
            print("\nThanks for playing!")
            break
        else:
            print("\nInvalid choice! Please choose 1, 2, or 3.")
            continue
        if not play_again():
            print("\nThanks for playing!")
            break
if __name__ == "__main__":
    main()
