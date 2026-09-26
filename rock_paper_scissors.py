import random
STANDARD_CHOICES = {
    "1": "rock",
    "2": "paper",
    "3": "scissors",
}
EXTENDED_CHOICES = {
    **STANDARD_CHOICES,
    "4": "lizard",
    "5": "spock",
}
STANDARD_MOVES = list(STANDARD_CHOICES.values())
EXTENDED_MOVES = list(EXTENDED_CHOICES.values())
BEATS = {
    "rock": {"scissors", "lizard"},
    "paper": {"rock", "spock"},
    "scissors": {"paper", "lizard"},
    "lizard": {"paper", "spock"},
    "spock": {"rock", "scissors"},
}
def display_title():
    print("\n" + "=" * 42)
    print("          ROCK PAPER SCISSORS")
    print("=" * 42)
def choose_game_mode():
    while True:
        choice = input("\nAdd Lizard & Spock? (y/n): ").strip().lower()
        if choice in ("y", "n"):
            return choice == "y"
        print("Invalid input! Enter y or n.")
def choose_personality():
    print("\nChoose computer personality:")
    print("  1. Balanced")
    print("  2. Adaptive")
    print("  3. Unpredictable")
    while True:
        choice = input("\nChoose: ").strip()
        if choice == "1":
            return "balanced"
        if choice == "2":
            return "adaptive"
        if choice == "3":
            return "unpredictable"
        print("Invalid choice! Please choose 1, 2, or 3.")
def display_choices(extended):
    choices = EXTENDED_CHOICES if extended else STANDARD_CHOICES
    print("\nChoose your move:")
    for key, move in choices.items():
        print(f"  {key}. {move.title()}")
def get_player_choice(extended):
    choices = EXTENDED_CHOICES if extended else STANDARD_CHOICES
    while True:
        display_choices(extended)
        choice = input("\nYour choice: ").strip()
        if choice in choices:
            return choices[choice]
        print(f"\nInvalid choice! Please choose 1-{len(choices)}.")
def get_round_winner(player, computer):
    if player == computer:
        return "draw"
    if computer in BEATS[player]:
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
def display_score(player_score, computer_score, win_streak):
    print(
        f"\nScore    : You {player_score}  |  "
        f"Computer {computer_score}"
    )
    print(f"Win streak: {win_streak}")
def counter_move(move, moves):
    possible_counters = [candidate for candidate in moves if move in BEATS[candidate]]
    return random.choice(possible_counters)
def choose_computer_move(player_history, moves, personality):
    if not player_history:
        return random.choice(moves)
    last_move = player_history[-1]
    if personality == "balanced":
        return random.choice(moves)
    if personality == "adaptive":
        counts = {move: player_history.count(move) for move in moves}
        most_common = max(counts, key=counts.get)
        if random.random() < 0.60:
            return counter_move(most_common, moves)
        return random.choice(moves)
    if random.random() < 0.30:
        return counter_move(last_move, moves)
    return random.choice(moves)
def play_round(extended, personality, player_history):
    player = get_player_choice(extended)
    moves = EXTENDED_MOVES if extended else STANDARD_MOVES
    computer = choose_computer_move(player_history, moves, personality)
    player_history.append(player)

    result = get_round_winner(player, computer)
    display_round_result(player, computer, result)
    return result
def play_single_game(extended, personality, player_history, win_streak):
    print("\n" + "-" * 42)
    print("                 SINGLE GAME")
    print("-" * 42)
    print(f"Computer personality: {personality.title()}")
    result = play_round(extended, personality, player_history)
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
def play_match(extended, personality, player_history, win_streak):
    print("\n" + "-" * 42)
    print("                 BEST OF...")
    print("-" * 42)
    total_rounds = get_match_length()
    player_score = 0
    computer_score = 0
    moves = EXTENDED_MOVES if extended else STANDARD_MOVES
    for round_number in range(1, total_rounds + 1):
        print("\n" + "=" * 42)
        print(f"                 ROUND {round_number}/{total_rounds}")
        print("=" * 42)
        player = get_player_choice(extended)
        computer = choose_computer_move(player_history, moves, personality)
        player_history.append(player)
        result = get_round_winner(player, computer)
        display_round_result(player, computer, result)
        if result == "player":
            player_score += 1
        elif result == "computer":
            computer_score += 1
        display_score(player_score, computer_score, win_streak)
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
    win_streak = 0
    player_history = []
    while True:
        display_title()
        print(f"\nCurrent win streak: {win_streak}")
        extended = choose_game_mode()
        personality = choose_personality()
        print("\n1. Single Game")
        print("2. Best of...")
        print("3. Exit")
        choice = input("\nChoose: ").strip()
        if choice == "1":
            result = play_single_game(
                extended, personality, player_history, win_streak
            )
        elif choice == "2":
            result = play_match(
                extended, personality, player_history, win_streak
            )
        elif choice == "3":
            print("\nThanks for playing!")
            break
        else:
            print("\nInvalid choice! Please choose 1, 2, or 3.")
            continue
        if record_result:
            record_result("rock_paper_scissors", result)
        if result == "win":
            win_streak += 1
            print(f"\nWin streak increased to {win_streak}!")
        else:
            if result == "loss":
                print("\nWin streak reset.")
            win_streak = 0
        if not play_again():
            print("\nThanks for playing!")
            break
if __name__ == "__main__":
    main()