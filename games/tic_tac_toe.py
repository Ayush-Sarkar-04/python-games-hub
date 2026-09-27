import random
from copy import deepcopy
from time import sleep
from engine.game import SessionConfig
from engine.result import GameResult
from engine.state import GameState
from engine.utils import play_again
EASY = "1"
MEDIUM = "2"
HARD = "3"
DIFFICULTY_MAP = {
    "easy": EASY,
    "medium": MEDIUM,
    "hard": HARD,
}
WINNING_COMBINATIONS = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
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
def get_winner(board):
    for a, b, c in WINNING_COMBINATIONS:
        if board[a] == board[b] == board[c] and board[a] != " ":
            return board[a]
    return None
def check_winner(board):
    return get_winner(board) is not None
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
def minimax(board, maximizing):
    winner = get_winner(board)
    if winner == "O":
        return 1
    if winner == "X":
        return -1
    empty_positions = get_empty_positions(board)
    if not empty_positions:
        return 0
    if maximizing:
        best_score = -float("inf")
        for position in empty_positions:
            board[position] = "O"
            score = minimax(board, False)
            board[position] = " "
            best_score = max(best_score, score)
        return best_score
    best_score = float("inf")
    for position in empty_positions:
        board[position] = "X"
        score = minimax(board, True)
        board[position] = " "
        best_score = min(best_score, score)
    return best_score
def find_best_move(board, personality="Balanced"):
    best_score = -float("inf")
    best_moves = []
    for position in get_empty_positions(board):
        board[position] = "O"
        score = minimax(board, False)
        board[position] = " "
        if score > best_score:
            best_score = score
            best_moves = [position]
        elif score == best_score:
            best_moves.append(position)
    if personality == "Aggressive":
        preferred = [
            position for position in (4, 0, 2, 6, 8)
            if position in best_moves
        ]
    elif personality == "Defensive":
        preferred = [
            position for position in (0, 2, 6, 8, 4)
            if position in best_moves
        ]
    else:
        preferred = best_moves
    preferred = preferred or best_moves
    return random.choice(preferred)
def choose_personality():
    personalities = {
        "1": "Balanced",
        "2": "Aggressive",
        "3": "Defensive",
    }
    while True:
        print("\nChoose Computer Personality")
        print("1. Balanced")
        print("2. Aggressive")
        print("3. Defensive")
        choice = input("\nChoose: ").strip()
        if choice in personalities:
            return personalities[choice]
        print("Invalid choice! Please choose 1, 2, or 3.")
def computer_move(board, difficulty, personality="Balanced"):
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
        if personality == "Aggressive":
            center = 4
            if center in empty_positions and random.random() < 0.7:
                return center
        elif personality == "Defensive":
            blocking_move = find_winning_move(board, "X")
            if blocking_move is not None:
                return blocking_move
        return random.choice(empty_positions)
    return find_best_move(board, personality)
def display_result(message):
    print("\n" + "=" * 42)
    print("                 GAME OVER")
    print("=" * 42)
    print(f"                 {message}")
    print("=" * 42)
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
def _hint_move(board, difficulty, personality):
    simulated_board = deepcopy(board)
    if difficulty == EASY:
        return random.choice(get_empty_positions(simulated_board))
    return computer_move(simulated_board, difficulty, personality)
def _display_replay(move_history, delay=0.0):
    board = [" "] * 9
    for move in move_history:
        board[move["position"]] = move["player"]
        display_board(board)
        if delay > 0:
            sleep(delay)
def _get_player_move(state, player, difficulty, personality, hint_used):
    while True:
        choice = input(
            f"Player {player}, choose a position (1-9)"
            f"{' or H for hint' if not hint_used else ''}: "
        ).strip().lower()
        if choice == "h" and not hint_used:
            hint = _hint_move(state.data["board"], difficulty, personality)
            print(f"Hint: position {hint + 1}.")
            return None, True
        try:
            position = int(choice) - 1
        except ValueError:
            print("Invalid input! Please enter a number from 1 to 9.")
            continue
        if position < 0 or position > 8:
            print("Invalid position! Please choose a number from 1 to 9.")
            continue
        if state.data["board"][position] != " ":
            print("Position already taken! Choose another position.")
            continue
        return position, hint_used
class TicTacToeGame:
    name = "Tic-Tac-Toe"
    description = "Classic 3x3 strategy game"
    def __init__(self):
        self.win_streak = 0
        self.best_streak = 0
    def setup(self, config: SessionConfig) -> GameState:
        if config.game != "tic_tac_toe":
            raise ValueError("TicTacToeGame requires game='tic_tac_toe'")
        if config.difficulty not in DIFFICULTY_MAP:
            raise ValueError(
                f"Unsupported Tic-Tac-Toe difficulty: {config.difficulty}"
            )
        player_mode = config.options.get("player_mode", "computer")
        if player_mode not in {"computer", "player"}:
            raise ValueError("player_mode must be 'computer' or 'player'")
        personality = config.options.get("personality", "Balanced")
        if personality not in {"Balanced", "Aggressive", "Defensive"}:
            raise ValueError("Unsupported Tic-Tac-Toe personality")
        return GameState(
            game="tic_tac_toe",
            status="ready",
            data={
                "board": [" "] * 9,
                "current_player": "X",
                "player_mode": player_mode,
                "personality": personality,
                "hint_used": False,
            },
            metadata={"difficulty": config.difficulty},
        )
    def play(self, state: GameState, config: SessionConfig) -> GameResult:
        difficulty = DIFFICULTY_MAP[config.difficulty]
        board = state.data["board"]
        player_mode = state.data["player_mode"]
        personality = state.data["personality"]
        state.set_status("playing")
        display_title()
        if player_mode == "computer":
            print(f"You are X. Computer is O. Personality: {personality}")
        if config.mode == "practice":
            print("Practice Mode: this session does not count toward competitive streaks.")
        outcome = "draw"
        message = "It's a draw!"
        for _ in range(9):
            display_board(board)
            player = state.data["current_player"]
            if player_mode == "computer" and player == "O":
                position = computer_move(board, difficulty, personality)
                print(f"Computer chooses position {position + 1}.")
            else:
                while True:
                    position, hint_used = _get_player_move(
                        state,
                        player,
                        difficulty,
                        personality,
                        state.data["hint_used"],
                    )
                    state.data["hint_used"] = hint_used
                    if position is not None:
                        break
            board[position] = player
            state.record_move({"player": player, "position": position})
            if check_winner(board):
                if player_mode == "computer" and player == "O":
                    outcome = "loss"
                    message = "Computer wins!"
                else:
                    outcome = "win"
                    message = f"Player {player} wins!"
                break
            state.data["current_player"] = "O" if player == "X" else "X"
        display_board(board)
        display_result(message)
        state.set_status(outcome)
        if config.is_competitive and player_mode == "computer":
            if outcome == "win":
                self.win_streak += 1
                self.best_streak = max(self.best_streak, self.win_streak)
            else:
                self.win_streak = 0
        result = GameResult(
            game="tic_tac_toe",
            outcome=outcome,
            difficulty=config.difficulty,
            mode=config.mode,
            moves=state.moves,
            metadata={
                "player_mode": player_mode,
                "personality": personality,
                "hint_used": state.data["hint_used"],
                "win_streak": self.win_streak,
                "best_streak": self.best_streak,
            },
        )
        return self._finish_with_optional_replay(result, state)
    def _finish_with_optional_replay(self, result, state):
        return result
def main(record_result=None):
    game = TicTacToeGame()
    while True:
        display_title()
        print("\n1. Player vs Computer")
        print("2. Player vs Player")
        print("3. Exit")
        choice = input("\nChoose: ").strip()
        if choice == "3":
            print("\nThanks for playing Tic-Tac-Toe!")
            break
        if choice not in {"1", "2"}:
            print("\nInvalid choice! Please choose 1, 2, or 3.")
            continue
        difficulty = choose_difficulty() if choice == "1" else MEDIUM
        personality = choose_personality() if choice == "1" else "Balanced"
        player_mode = "computer" if choice == "1" else "player"
        config = SessionConfig(
            game="tic_tac_toe",
            difficulty={"1": "easy", "2": "medium", "3": "hard"}[difficulty],
            options={"player_mode": player_mode, "personality": personality},
        )
        result = game.play(game.setup(config), config)
        if record_result:
            record_result("tic_tac_toe", result.outcome)
        print(f"Win streak: {game.win_streak} | Best: {game.best_streak}")
        if not play_again():
            print("\nThanks for playing Tic-Tac-Toe!")
            break
if __name__ == "__main__":
    main()