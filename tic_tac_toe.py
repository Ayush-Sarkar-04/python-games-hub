import random

EASY = "1"
MEDIUM = "2"
HARD = "3"

WINNING_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6)
]
def display_title():
    print("\n" + "=" * 42)
    print("              TIC-TAC-TOE")
    print("=" * 42)
def display_board(board):
    print()
    cells = [
        str(index + 1) if value == " " else value
        for index, value in enumerate(board)
    ]
    print("          |       |")
    print(f"       {cells[0]:^5}|{cells[1]:^7}|{cells[2]:^5}")
    print("     ------+-------+------")
    print(f"       {cells[3]:^5}|{cells[4]:^7}|{cells[5]:^5}")
    print("     ------+-------+------")
    print(f"       {cells[6]:^5}|{cells[7]:^7}|{cells[8]:^5}")
    print()
def check_winner(board):
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return True
    return False
def get_player_move(board, player):
    while True:
        choice = input(f"Player {player}, choose a position (1-9): ").strip()
        try:
            position = int(choice) - 1
        except ValueError:
            print("Invalid input! Please enter a number from 1 to 9.")
            continue
        if position < 0 or position > 8:
            print("Invalid position! Please choose a number from 1 to 9.")
            continue
        if board[position] != " ":
            print("Position already taken! Choose another position.")
            continue
        return position
def get_empty_positions(board):
    return [i for i in range(9) if board[i] == " "]
def find_winning_move(board, player):
    for position in get_empty_positions(board):
        board[position] = player
        if check_winner(board):
            board[position] = " "
            return position
        board[position] = " "
    return None
def computer_move(board, difficulty):
    empty_positions = get_empty_positions(board)
    if difficulty == EASY:
        return random.choice(empty_positions)
    winning_move = find_winning_move(board, "O")
    if winning_move is not None:
        return winning_move
    blocking_move = find_winning_move(board, "X")
    if blocking_move is not None:
        return blocking_move
    if difficulty == MEDIUM:
        return random.choice(empty_positions)
    if board[4] == " ":
        return 4
    corners = [0, 2, 6, 8]
    free_corners = [corner for corner in corners if board[corner] == " "]
    if free_corners:
        return random.choice(free_corners)
    return random.choice(empty_positions)
def display_result(message):
    print("\n" + "=" * 42)
    print("                 GAME OVER")
    print("=" * 42)
    print(f"                 {message}")
    print("=" * 42)
def play_game(mode, difficulty=None):
    board = [" "] * 9
    player = "X"
    for _ in range(9):
        display_board(board)
        if mode == "computer" and player == "O":
            position = computer_move(board, difficulty)
            print(f"Computer chooses position {position + 1}.")
        else:
            position = get_player_move(board, player)
        board[position] = player
        if check_winner(board):
            display_board(board)
            if mode == "computer" and player == "O":
                display_result("Computer wins!")
                return "loss"
            display_result(f"Player {player} wins!")
            return "win"
        if player == "X":
            player = "O"
        else:
            player = "X"
    display_board(board)
    display_result("It's a draw!")
    return "draw"
def choose_difficulty():
    while True:
        print("\n" + "-" * 42)
        print("              CHOOSE DIFFICULTY")
        print("-" * 42)
        print("1. Easy")
        print("2. Medium")
        print("3. Hard")
        difficulty = input("\nChoose: ").strip()
        if difficulty in (EASY, MEDIUM, HARD):
            return difficulty
        print("Invalid choice! Please choose 1, 2, or 3.")
def play_again():
    while True:
        choice = input("\nPlay again? (y/n): ").strip().lower()
        if choice in ("y", "n"):
            return choice == "y"
        print("Invalid input! Enter y or n.")
def main(record_result=None):
    while True:
        display_title()
        print("\n1. Player vs Computer")
        print("2. Player vs Player")
        print("3. Exit")
        choice = input("\nChoose: ").strip()
        if choice == "1":
            difficulty = choose_difficulty()
            print("\nYou are X. Computer is O.")
            result = play_game("computer", difficulty)
            if record_result:
                record_result("tic_tac_toe", result)
        elif choice == "2":
            print("\nPlayer X goes first.")
            result = play_game("player")
            if record_result:
                record_result("tic_tac_toe", result)
        elif choice == "3":
            print("\nThanks for playing Tic-Tac-Toe!")
            break
        else:
            print("\nInvalid choice! Please choose 1, 2, or 3.")
            continue
        if not play_again():
            print("\nThanks for playing Tic-Tac-Toe!")
            break
if __name__ == "__main__":
    main()
