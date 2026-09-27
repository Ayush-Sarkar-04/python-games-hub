import math
import random
ROWS = 6
COLUMNS = 7
EMPTY = " "
PLAYER = "X"
COMPUTER = "O"
EASY = "1"
MEDIUM = "2"
HARD = "3"
WIN_SCORE = 100
THREE_SCORE = 8
TWO_SCORE = 3
OPPONENT_THREE_PENALTY = 7
DIFFICULTIES = {
    EASY: "Easy",
    MEDIUM: "Medium",
    HARD: "Hard",
}
def display_title():
    print("\n" + "=" * 50)
    print("                 CONNECT FOUR")
    print("=" * 50)
    print("              Connect 4 to win!")
    print("=" * 50)
def create_board():
    return [[EMPTY for _ in range(COLUMNS)] for _ in range(ROWS)]
def display_board(board):
    print()
    print("       " + "   ".join(str(column) for column in range(1, COLUMNS + 1)))
    print("     " + "---+" * (COLUMNS - 1) + "---")
    for row_index, row in enumerate(board):
        print("     " + " | ".join(f" {cell} " for cell in row))
        if row_index < len(board) - 1:
            print("     " + "---+" * (COLUMNS - 1) + "---")
    print("     " + "---+" * (COLUMNS - 1) + "---")
    print()
def get_valid_columns(board):
    return [column for column in range(COLUMNS) if board[0][column] == EMPTY]
def get_next_open_row(board, column):
    for row in range(ROWS - 1, -1, -1):
        if board[row][column] == EMPTY:
            return row
    return None
def check_winner(board, piece):
    for row in range(ROWS):
        for column in range(COLUMNS - 3):
            if all(board[row][column + offset] == piece for offset in range(4)):
                return True
    for row in range(ROWS - 3):
        for column in range(COLUMNS):
            if all(board[row + offset][column] == piece for offset in range(4)):
                return True
    for row in range(ROWS - 3):
        for column in range(COLUMNS - 3):
            if all(
                board[row + offset][column + offset] == piece
                for offset in range(4)
            ):
                return True
    for row in range(3, ROWS):
        for column in range(COLUMNS - 3):
            if all(
                board[row - offset][column + offset] == piece
                for offset in range(4)
            ):
                return True
    return False
def board_full(board):
    return not get_valid_columns(board)
def get_player_move(board, player):
    while True:
        choice = input(
            f"Player {player}, choose a column (1-{COLUMNS}): "
        ).strip()
        try:
            column = int(choice) - 1
        except ValueError:
            print(f"Invalid input! Please enter a number from 1 to {COLUMNS}.")
            continue
        if column not in range(COLUMNS):
            print(f"Please choose a column from 1 to {COLUMNS}.")
            continue
        if column not in get_valid_columns(board):
            print("That column is full! Choose another column.")
            continue
        return column
def simulate_move(board, column, piece):
    row = get_next_open_row(board, column)
    if row is None:
        return None
    board[row][column] = piece
    return row
def score_window(window, piece):
    opponent = COMPUTER if piece == COMPUTER else PLAYER
    score = 0
    if window.count(piece) == 4:
        score += WIN_SCORE
    elif window.count(piece) == 3 and window.count(EMPTY) == 1:
        score += THREE_SCORE
    elif window.count(piece) == 2 and window.count(EMPTY) == 2:
        score += TWO_SCORE
    if window.count(opponent) == 3 and window.count(EMPTY) == 1:
        score -= OPPONENT_THREE_PENALTY
    return score
def evaluate_board(board, piece):
    score = 0
    center_column = [board[row][COLUMNS // 2] for row in range(ROWS)]
    score += center_column.count(piece) * 4
    for row in range(ROWS):
        for column in range(COLUMNS - 3):
            window = [
                board[row][column + offset]
                for offset in range(4)
            ]
            score += score_window(window, piece)
    for row in range(ROWS - 3):
        for column in range(COLUMNS):
            window = [
                board[row + offset][column]
                for offset in range(4)
            ]
            score += score_window(window, piece)
    for row in range(ROWS - 3):
        for column in range(COLUMNS - 3):
            window = [
                board[row + offset][column + offset]
                for offset in range(4)
            ]
            score += score_window(window, piece)
    for row in range(3, ROWS):
        for column in range(COLUMNS - 3):
            window = [
                board[row - offset][column + offset]
                for offset in range(4)
            ]
            score += score_window(window, piece)
    return score
def find_immediate_move(board, piece):
    for column in get_valid_columns(board):
        test_board = [row[:] for row in board]
        simulate_move(test_board, column, piece)
        if check_winner(test_board, piece):
            return column
    return None
def minimax(board, depth, maximizing):
    valid_columns = get_valid_columns(board)
    if check_winner(board, COMPUTER):
        return None, 1000000 + depth
    if check_winner(board, PLAYER):
        return None, -1000000 - depth
    if not valid_columns or depth == 0:
        return None, evaluate_board(board, COMPUTER)

    if maximizing:
        best_score = -math.inf
        best_columns = []

        for column in valid_columns:
            test_board = [row[:] for row in board]
            simulate_move(test_board, column, COMPUTER)
            _, score = minimax(test_board, depth - 1, False)

            if score > best_score:
                best_score = score
                best_columns = [column]
            elif score == best_score:
                best_columns.append(column)
        return random.choice(best_columns), best_score
    best_score = math.inf
    best_columns = []
    for column in valid_columns:
        test_board = [row[:] for row in board]
        simulate_move(test_board, column, PLAYER)
        _, score = minimax(test_board, depth - 1, True)
        if score < best_score:
            best_score = score
            best_columns = [column]
        elif score == best_score:
            best_columns.append(column)
    return random.choice(best_columns), best_score
def computer_move(board, difficulty):
    valid_columns = get_valid_columns(board)
    if difficulty == EASY:
        return random.choice(valid_columns)
    winning_move = find_immediate_move(board, COMPUTER)
    if winning_move is not None:
        return winning_move
    blocking_move = find_immediate_move(board, PLAYER)
    if blocking_move is not None:
        return blocking_move
    if difficulty == MEDIUM:
        center = COLUMNS // 2
        if center in valid_columns and random.random() < 0.7:
            return center
        return random.choice(valid_columns)
    best_column, _ = minimax(board, 4, True)
    if best_column is not None:
        return best_column
    return random.choice(valid_columns)
def display_result(message):
    print("\n" + "=" * 50)
    print("                  GAME OVER")
    print("=" * 50)
    print(f"                  {message}")
    print("=" * 50)
def choose_difficulty():
    while True:
        print("\n" + "-" * 50)
        print("                CHOOSE DIFFICULTY")
        print("-" * 50)
        print("  1. Easy")
        print("  2. Medium")
        print("  3. Hard")
        choice = input("\nChoose: ").strip()
        if choice in DIFFICULTIES:
            return choice
        print("Invalid choice! Please choose 1, 2, or 3.")
def choose_first_player(mode):
    print("\nWho goes first?")
    if mode == "computer":
        print("  1. Player")
        print("  2. Computer")
    else:
        print("  1. Player X")
        print("  2. Player O")
    while True:
        choice = input("\nChoose: ").strip()
        if choice in ("1", "2"):
            if mode == "computer":
                return PLAYER if choice == "1" else COMPUTER
            return PLAYER if choice == "1" else "O"
        print("Invalid choice! Please choose 1 or 2.")
def play_game(mode, difficulty=None, first_player=PLAYER):
    board = create_board()
    current_player = first_player
    turn_number = 1
    while True:
        display_board(board)
        print(f"Turn: {turn_number}")
        if mode == "computer" and current_player == COMPUTER:
            column = computer_move(board, difficulty)
            simulate_move(board, column, COMPUTER)
            print(f"Computer chooses column {column + 1}.")
        else:
            column = get_player_move(board, current_player)
            simulate_move(board, column, current_player)
        if check_winner(board, current_player):
            display_board(board)
            if mode == "computer" and current_player == COMPUTER:
                display_result(
                    f"Computer wins in {turn_number} turns!"
                )
                return "loss"
            display_result(
                f"Player {current_player} wins in {turn_number} turns!"
            )
            return "win"
        if board_full(board):
            display_board(board)
            display_result(f"It's a draw after {turn_number} turns!")
            return "draw"
        current_player = COMPUTER if current_player == PLAYER else PLAYER
        turn_number += 1
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
            first_player = choose_first_player("computer")
            if first_player == PLAYER:
                print("\nYou are X. Computer is O.")
            else:
                print("\nComputer is X. You are O.")

            result = play_game("computer", difficulty, first_player)
            if record_result:
                record_result("connect_four", result)
        elif choice == "2":
            first_player = choose_first_player("player")
            print(f"\nPlayer {first_player} goes first.")

            result = play_game("player", first_player=first_player)

            if record_result:
                record_result("connect_four", result)

        elif choice == "3":
            print("\nThanks for playing Connect Four!")
            break
        else:
            print("\nInvalid choice! Please choose 1, 2, or 3.")
            continue
        if not play_again():
            print("\nThanks for playing Connect Four!")
            break
if __name__ == "__main__":
    main()